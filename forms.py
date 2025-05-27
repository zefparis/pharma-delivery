from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, FloatField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], 
                       render_kw={"placeholder": "votre@email.com", "class": "form-control"})
    password = PasswordField('Mot de passe', validators=[DataRequired()],
                           render_kw={"placeholder": "Votre mot de passe", "class": "form-control"})

class RegisterForm(FlaskForm):
    name = StringField('Nom complet', validators=[DataRequired(), Length(min=2, max=100)],
                      render_kw={"placeholder": "Votre nom complet", "class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()],
                       render_kw={"placeholder": "votre@email.com", "class": "form-control"})
    phone = StringField('Téléphone', validators=[Optional()],
                       render_kw={"placeholder": "+243 XXX XXX XXX", "class": "form-control"})
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)],
                           render_kw={"placeholder": "Minimum 6 caractères", "class": "form-control"})

class CheckoutForm(FlaskForm):
    delivery_address = TextAreaField('Adresse de livraison', validators=[DataRequired()],
                                   render_kw={"placeholder": "Adresse complète pour la livraison", "class": "form-control", "rows": "3"})
    payment_method = SelectField('Méthode de paiement', 
                               choices=[('orange', 'Orange Money'), ('airtel', 'Airtel Money'), ('africell', 'Africell Money')],
                               validators=[DataRequired()], render_kw={"class": "form-select"})
    payment_phone = StringField('Numéro de paiement mobile', validators=[DataRequired()],
                              render_kw={"placeholder": "+243 XXX XXX XXX", "class": "form-control"})
    notes = TextAreaField('Notes pour la livraison (optionnel)',
                         render_kw={"placeholder": "Instructions spéciales...", "class": "form-control", "rows": "2"})

class ContactForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired()],
                      render_kw={"placeholder": "Votre nom", "class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()],
                       render_kw={"placeholder": "votre@email.com", "class": "form-control"})
    phone = StringField('Téléphone', validators=[Optional()],
                       render_kw={"placeholder": "+243 XXX XXX XXX", "class": "form-control"})
    subject = StringField('Sujet', validators=[DataRequired()],
                         render_kw={"placeholder": "Sujet de votre message", "class": "form-control"})
    message = TextAreaField('Message', validators=[DataRequired()],
                          render_kw={"placeholder": "Votre message...", "class": "form-control", "rows": "5"})

class ProductForm(FlaskForm):
    name = StringField('Nom du produit', validators=[DataRequired()],
                      render_kw={"class": "form-control"})
    description = TextAreaField('Description',
                              render_kw={"class": "form-control", "rows": "4"})
    price = FloatField('Prix (CDF)', validators=[DataRequired(), NumberRange(min=0)],
                      render_kw={"class": "form-control"})
    stock_quantity = IntegerField('Quantité en stock', validators=[DataRequired(), NumberRange(min=0)],
                                render_kw={"class": "form-control"})
    category_id = SelectField('Catégorie', coerce=int, validators=[DataRequired()],
                            render_kw={"class": "form-select"})
    image_url = StringField('URL de l\'image',
                          render_kw={"class": "form-control"})
    laboratory = StringField('Laboratoire',
                           render_kw={"class": "form-control"})
    dosage = StringField('Dosage',
                        render_kw={"class": "form-control"})
    form_type = StringField('Forme',
                           render_kw={"class": "form-control", "placeholder": "Comprimés, gélules, sirop..."})
    prescription_required = BooleanField('Prescription requise',
                                       render_kw={"class": "form-check-input"})
    is_active = BooleanField('Produit actif',
                           render_kw={"class": "form-check-input"})

class AddToCartForm(FlaskForm):
    product_id = HiddenField('Product ID', validators=[DataRequired()])
    quantity = IntegerField('Quantité', validators=[DataRequired(), NumberRange(min=1)], default=1,
                          render_kw={"class": "form-control", "min": "1"})

class UpdateCartForm(FlaskForm):
    cart_item_id = HiddenField('Cart Item ID', validators=[DataRequired()])
    quantity = IntegerField('Quantité', validators=[DataRequired(), NumberRange(min=0)],
                          render_kw={"class": "form-control", "min": "0"})
