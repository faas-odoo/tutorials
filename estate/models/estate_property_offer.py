from odoo import fields, models, api, exceptions
import datetime

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate property offer"
    price = fields.Float('Price')
    status = fields.Selection(string='Status',
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy = False, readonly= True)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required = True)
    property_id = fields.Many2one(comodel_name="estate.property", string="Property", required = True)
    validity = fields.Integer('Validity', default = 7)
    date_deadline = fields.Date(string='Deadline', compute='_deadline_compute', inverse = '_inverse_validity')
    property_type_id = fields.Many2one(related="property_id.property_type_id", store = True)
    _order = "price desc"
    
    _sql_constraints = [
        ('check_offer_price', 'CHECK(price >= 0)',
         'The offer price should be > 0')
    ]
    
    @api.model
    def create(self, vals):
        if self.env['estate.property'].browse(vals['property_id']).best_price >= vals['price']:
            raise exceptions.UserError("Greater offer already exists!")
        return super(EstatePropertyOffer, self).create(vals)
    
        
    @api.depends("validity", "create_date")
    def _deadline_compute(self):
        for record in self:
            if record.create_date:
                create_date = fields.Date.from_string(record.create_date)
                record.date_deadline = create_date + datetime.timedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.context_today(record) + datetime.timedelta(days=record.validity)
    
    
    def _inverse_validity(self):
        for record in self:
            if record.date_deadline and record.create_date:
                create_date = fields.Date.from_string(record.create_date)
                deadline_date = fields.Date.from_string(record.date_deadline)
                record.validity = (deadline_date - create_date).days
            else:
                record.validity = 0
    
    
    def offer_confirm(self):
        if self.property_id.state == 'offer accepted':
            raise exceptions.UserError("One offer already accepted")
        
        self.property_id.state = 'offer accepted'
        self.status = 'accepted'
        self.property_id.buyer_id = self.partner_id
        self.property_id.selling_price = self.price
        
    
    def offer_cancel(self):
        if self.status == 'accepted': 
            raise exceptions.UserError("Cannot refuse an acepted offer")
        
        self.status = 'refused'