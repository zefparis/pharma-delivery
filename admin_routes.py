from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app import app, db
from models import User, Product, Category, Order, OrderItem, SupportMessage, OrderStatus
from forms import ProductForm
import logging

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès non autorisé.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Statistiques
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).count()
    unread_messages = SupportMessage.query.filter_by(is_read=False).count()
    
    # Commandes récentes
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Produits en rupture de stock
    low_stock_products = Product.query.filter(Product.stock_quantity <= 5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         unread_messages=unread_messages,
                         recent_orders=recent_orders,
                         low_stock_products=low_stock_products)

@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Product.query
    if search:
        query = query.filter(Product.name.contains(search) | 
                           Product.laboratory.contains(search))
    
    products = query.order_by(Product.created_at.desc())\
                   .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/products.html', products=products, search_query=search)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_product():
    form = ProductForm()
    
    # Charger les catégories
    categories = Category.query.all()
    form.category_id.choices = [(cat.id, cat.name) for cat in categories]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock_quantity=form.stock_quantity.data,
            category_id=form.category_id.data,
            image_url=form.image_url.data,
            laboratory=form.laboratory.data,
            dosage=form.dosage.data,
            form=form.form_type.data,
            prescription_required=form.prescription_required.data,
            is_active=form.is_active.data
        )
        db.session.add(product)
        db.session.commit()
        
        flash('Produit ajouté avec succès!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/products.html', form=form, editing=False)

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    
    # Charger les catégories
    categories = Category.query.all()
    form.category_id.choices = [(cat.id, cat.name) for cat in categories]
    
    if form.validate_on_submit():
        form.populate_obj(product)
        product.form = form.form_type.data  # Mapping spécial pour éviter le conflit avec 'form'
        db.session.commit()
        
        flash('Produit modifié avec succès!', 'success')
        return redirect(url_for('admin_products'))
    
    # Pré-remplir le formulaire
    form.form_type.data = product.form
    
    return render_template('admin/products.html', form=form, editing=True, product=product)

@app.route('/admin/products/delete/<int:product_id>')
@login_required
@admin_required
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False  # Soft delete
    db.session.commit()
    
    flash('Produit désactivé avec succès!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Order.query
    if status_filter:
        query = query.filter_by(status=OrderStatus(status_filter))
    
    orders = query.order_by(Order.created_at.desc())\
                 .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/orders.html', orders=orders, 
                         status_filter=status_filter, 
                         order_statuses=OrderStatus)

@app.route('/admin/orders/update_status/<int:order_id>/<string:new_status>')
@login_required
@admin_required
def admin_update_order_status(order_id, new_status):
    order = Order.query.get_or_404(order_id)
    
    try:
        order.status = OrderStatus(new_status)
        db.session.commit()
        flash(f'Statut de la commande #{order_id} mis à jour.', 'success')
    except ValueError:
        flash('Statut invalide.', 'danger')
    
    return redirect(url_for('admin_orders'))

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(User.name.contains(search) | 
                           User.email.contains(search))
    
    users = query.order_by(User.created_at.desc())\
                .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html', users=users, search_query=search)

@app.route('/admin/messages')
@login_required
@admin_required
def admin_messages():
    page = request.args.get('page', 1, type=int)
    messages = SupportMessage.query.order_by(SupportMessage.created_at.desc())\
                                  .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/messages/mark_read/<int:message_id>')
@login_required
@admin_required
def admin_mark_message_read(message_id):
    message = SupportMessage.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    
    flash('Message marqué comme lu.', 'success')
    return redirect(url_for('admin_messages'))
