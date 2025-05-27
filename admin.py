from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app import db
from models import User, Product, Order

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès non autorisé', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    # Get dashboard statistics
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         recent_orders=recent_orders)

@bp.route('/products')
@login_required
@admin_required
def products():
    products = Product.query.order_by(Product.name).all()
    return render_template('admin/products.html', products=products)

@bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            category=request.form['category'],
            manufacturer=request.form['manufacturer'],
            stock_quantity=int(request.form['stock_quantity']),
            image_url=request.form.get('image_url', ''),
            prescription_required=bool(request.form.get('prescription_required')),
            active_ingredient=request.form.get('active_ingredient', ''),
            dosage=request.form.get('dosage', ''),
            featured=bool(request.form.get('featured'))
        )
        
        db.session.add(product)
        db.session.commit()
        flash('Produit ajouté avec succès!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/products.html', add_mode=True)

@bp.route('/products/<int:product_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    product.name = request.form['name']
    product.description = request.form['description']
    product.price = float(request.form['price'])
    product.category = request.form['category']
    product.manufacturer = request.form['manufacturer']
    product.stock_quantity = int(request.form['stock_quantity'])
    product.image_url = request.form.get('image_url', '')
    product.prescription_required = bool(request.form.get('prescription_required'))
    product.active_ingredient = request.form.get('active_ingredient', '')
    product.dosage = request.form.get('dosage', '')
    product.featured = bool(request.form.get('featured'))
    product.available = bool(request.form.get('available'))
    
    db.session.commit()
    flash('Produit modifié avec succès!', 'success')
    return redirect(url_for('admin.products'))

@bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Produit supprimé avec succès!', 'success')
    return redirect(url_for('admin.products'))

@bp.route('/orders')
@login_required
@admin_required
def orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@bp.route('/orders/<int:order_id>/update_status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    flash('Statut de commande mis à jour!', 'success')
    return redirect(url_for('admin.orders'))
