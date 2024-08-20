from odoo import fields, models, api, exceptions
from odoo.tools.float_utils import float_compare
import logging

import datetime

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate properties"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char('Title', required = True)
    description = fields.Text('Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date('Date availability', copy=False, default = datetime.date.today()+ datetime.timedelta(weeks=12))
    expected_price = fields.Float('Expected Price',required = True)
    selling_price = fields.Float('Selling Price', readonly =True, copy = False)
    bedrooms = fields.Integer('Bedrooms', default = 2)
    living_area = fields.Integer('Living Area')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area')
    garden_orientation = fields.Selection(string='Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help="Direction Facing")
    
    active = fields.Boolean('Active', default = True)

    state = fields.Selection(string='State',
        selection=[('new', ' New'), ('offer received', 'Offer Received'), ('offer accepted', 'Offer Accepted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')],
        help="Property State", default = 'new', store=True, readonly= True, compute="_compute_offer_received")
    
    property_type_id = fields.Many2one(comodel_name="estate.property.type", string="Property type")
    buyer_id = fields.Many2one(comodel_name="res.partner", string="Buyer", readonly= True)
    sales_person_id = fields.Many2one(comodel_name="res.users", string="Sales Person", default=lambda self: self.env.user)
    tag_ids = fields.Many2many(comodel_name="estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offer")
    total_area = fields.Float(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")
    _order = "id desc"
    
    _sql_constraints = [
        ('expected_price_pos', 'CHECK(expected_price > 0)', 'Expected price should be positive'),
        ('selling_price_pos', 'CHECK(selling_price > 0)', 'Selling price should be positive'),
    ]
    
    
    @api.ondelete(at_uninstall=False)
    def _unlink_except_active_properties(self):
        for record in self:
            if record.state not in ['new', 'cancelled']:
                raise exceptions.UserError("Can't delete an active property!")
    
    
    @api.constrains('selling_price','expected_price')
    def selling_price_constraints(self):
        if self.state == 'new' or self.state == 'offer received' or not self.selling_price:
            return
        
        for record in self:
            x = float_compare(100 * record.selling_price , 90 * record.expected_price, precision_digits=5)
            if x == -1:
                raise exceptions.ValidationError("Selling price cannot be this low maaan, please respect")
    
    
    @api.depends('offer_ids')
    def _compute_offer_received(self):
        for record in self:
            if record.state == 'new' and record.offer_ids and len(record.offer_ids) > 0: 
                record.state = 'offer received'
        return
            
    
    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area
            
    
    @api.depends("offer_ids")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0
        
        
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = ""
        
        
    def sold_action(self):
        if self.state == 'cancel':
            raise exceptions.UserError("Cancelled properties cannot be sold")
        
        print("sold 1 called")
        self.state = 'sold'
        
    
    def cancel_action(self):
        if self.state == 'sold':
            raise exceptions.UserError("Sold properties cannot be cancelled")
        
        self.state = 'cancel'