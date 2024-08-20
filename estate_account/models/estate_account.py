from odoo import models, Command

class EstateAccount(models.Model):
    _description = "Real Estate properties inherited"
    _inherit = ['estate.property']
    
    def sold_action(self):
        partner_id = self.buyer_id
        move_type = 'out_invoice'
        self.env['account.move'].create({
            'move_type': move_type,
            'partner_id': partner_id.id,
            'invoice_line_ids': [
                Command.create(
                    {'name': 'Property Price', 'price_unit': self.selling_price, 'quantity': 1}
                ),
                Command.create(
                    {'name': 'Comission', 'price_unit': (self.selling_price * 6) / 100.0, 'quantity': 1}
                ),
                Command.create(
                    {'name': 'Administrative Fees', 'price_unit': 100.0, 'quantity': 1}
                )]
        })

        return super().sold_action()