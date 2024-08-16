from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate property type"
    name = fields.Char('Title', required = True)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Type already exists!"),
    ]