from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import User, Product, Category, CartItem, Order, OrderItem, SupportMessage, OrderStatus
from forms import LoginForm, RegisterForm, CheckoutForm, ContactForm, AddToCartForm, UpdateCartForm
import logging

@app.route('/')
def index():
    # Récupérer les produits en vedette (6 premiers produits actifs)
    featured_products = Product.query.filter_by(is_active=True).limit(6).all()
    categories = Category.query.all()
    return render_template('index.html', featured_products=featured_products, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Connexion réussie!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Vérifier si l'email existe déjà
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Cet email est déjà utilisé.', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Créer le nouvel utilisateur
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('index'))

@app.route('/catalog')
def catalog():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    
    query = Product.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(Product.name.contains(search) | 
                           Product.description.contains(search) |
                           Product.laboratory.contains(search))
    
    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.all()
    
    return render_template('products/catalog.html', 
                         products=products, 
                         categories=categories,
                         current_category=category_id,
                         search_query=search)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddToCartForm()
    form.product_id.data = product_id
    
    # Produits similaires de la même catégorie
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product_id,
        Product.is_active == True
    ).limit(4).all()
    
    return render_template('products/detail.html', 
                         product=product, 
                         form=form,
                         related_products=related_products)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    form = AddToCartForm()
    if form.validate_on_submit():
        product_id = form.product_id.data
        quantity = form.quantity.data
        
        product = Product.query.get_or_404(product_id)
        
        # Vérifier le stock
        if quantity > product.stock_quantity:
            flash(f'Stock insuffisant. Disponible: {product.stock_quantity}', 'warning')
            return redirect(url_for('product_detail', product_id=product_id))
        
        # Vérifier si le produit est déjà dans le panier
        existing_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        
        if existing_item:
            new_quantity = existing_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                flash(f'Stock insuffisant. Quantité max: {product.stock_quantity}', 'warning')
                return redirect(url_for('product_detail', product_id=product_id))
            existing_item.quantity = new_quantity
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        flash('Produit ajouté au panier!', 'success')
    
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart/index.html', cart_items=cart_items, total=total)

@app.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    form = UpdateCartForm()
    if form.validate_on_submit():
        cart_item_id = form.cart_item_id.data
        quantity = form.quantity.data
        
        cart_item = CartItem.query.filter_by(
            id=cart_item_id,
            user_id=current_user.id
        ).first_or_404()
        
        if quantity == 0:
            db.session.delete(cart_item)
            flash('Produit retiré du panier.', 'info')
        else:
            if quantity > cart_item.product.stock_quantity:
                flash(f'Stock insuffisant pour {cart_item.product.name}', 'warning')
                return redirect(url_for('cart'))
            cart_item.quantity = quantity
            flash('Panier mis à jour.', 'success')
        
        db.session.commit()
    
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:cart_item_id>')
@login_required
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.filter_by(
        id=cart_item_id,
        user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Produit retiré du panier.', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('catalog'))
    
    form = CheckoutForm()
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if form.validate_on_submit():
        # Créer la commande
        order = Order(
            user_id=current_user.id,
            total_amount=total,
            delivery_address=form.delivery_address.data,
            payment_method=form.payment_method.data,
            payment_phone=form.payment_phone.data,
            notes=form.notes.data
        )
        db.session.add(order)
        db.session.flush()  # Pour obtenir l'ID de la commande
        
        # Créer les items de commande
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
            
            # Réduire le stock
            cart_item.product.stock_quantity -= cart_item.quantity
        
        # Vider le panier
        CartItem.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        
        flash('Commande passée avec succès!', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    return render_template('orders/checkout.html', 
                         form=form, 
                         cart_items=cart_items, 
                         total=total)

@app.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('orders/confirmation.html', order=order)

@app.route('/orders')
@login_required
def user_orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id)\
                       .order_by(Order.created_at.desc())\
                       .paginate(page=page, per_page=10, error_out=False)
    return render_template('orders/tracking.html', orders=orders)

@app.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        message = SupportMessage(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(message)
        db.session.commit()
        
        flash('Votre message a été envoyé. Nous vous répondrons bientôt!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html', form=form)

@app.context_processor
def inject_cart_count():
    if current_user.is_authenticated:
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    else:
        cart_count = 0
    return dict(cart_count=cart_count)

@app.template_filter('currency')
def currency_filter(amount):
    """Format currency for CDF"""
    return f"{amount:,.0f} CDF"
