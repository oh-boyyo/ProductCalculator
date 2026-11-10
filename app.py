from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP
from flask import Flask, render_template, request

app = Flask(__name__)


def money(value):
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_costs(products, final_amount):
    """Calculate packages, leftovers, and total spending for every material."""
    total_cost = Decimal('0.00')
    for product in products:
        units_needed = product['final_count'] * final_amount
        packs = (units_needed + product['per_pack'] - 1) // product['per_pack']
        product['total_units'] = units_needed
        product['packs'] = packs
        product['leftover'] = packs * product['per_pack'] - units_needed
        product['total_cost'] = money(packs * product['pack_cost'])
        total_cost += product['total_cost']
    return money(total_cost)


def get_decimal(value, label):
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, TypeError):
        raise ValueError(f'{label} must be a number.')
    if not number.is_finite() or number < 0:
        raise ValueError(f'{label} cannot be negative.')
    return number


def get_whole(value, label, minimum=0):
    number = get_decimal(value, label)
    if number != number.to_integral_value() or number < minimum:
        raise ValueError(f'{label} must be a whole number of at least {minimum}.')
    return int(number)


@app.route('/', methods=['GET', 'POST'])
def index():
    # Data is received from the current user's form only; nothing is stored globally.
    form = {
        'final_name': '', 'final_amount': '0', 'price': '0.00',
        'materials': [{'name': '', 'per_pack': '', 'pack_cost': '', 'final_count': ''}]
    }
    result = None
    error = None

    if request.method == 'POST':
        indices = request.form.getlist('material_id')
        if len(indices) > 100:
            error = 'Please enter no more than 100 materials.'
            indices = indices[:100]
        materials = []
        for material_id in indices:
            materials.append({
                'name': request.form.get(f'name_{material_id}', '').strip(),
                'per_pack': request.form.get(f'per_pack_{material_id}', '').strip(),
                'pack_cost': request.form.get(f'pack_cost_{material_id}', '').strip(),
                'final_count': request.form.get(f'final_count_{material_id}', '').strip(),
            })
        form = {
            'final_name': request.form.get('final_name', '').strip(),
            'final_amount': request.form.get('final_amount', '').strip(),
            'price': request.form.get('price', '').strip(),
            'materials': materials or [{'name': '', 'per_pack': '', 'pack_cost': '', 'final_count': ''}],
        }
        if error is None:
            try:
                if not form['final_name']:
                    raise ValueError('Enter a name for your finished product.')
                if not materials:
                    raise ValueError('Add at least one material.')
                final_amount = get_whole(form['final_amount'], 'Final amount', 0)
                price = money(get_decimal(form['price'], 'Selling price'))
                if price != get_decimal(form['price'], 'Selling price'):
                    raise ValueError('Selling price must have at most two decimal places.')
                products = []
                for i, material in enumerate(materials, 1):
                    if not material['name']:
                        raise ValueError(f'Enter a name for material {i}.')
                    pack_cost = get_decimal(material['pack_cost'], f'Material {i} package cost')
                    if money(pack_cost) != pack_cost:
                        raise ValueError(f'Material {i} package cost must have at most two decimal places.')
                    products.append({
                        'name': material['name'],
                        'per_pack': get_whole(material['per_pack'], f'Material {i} units per pack', 1),
                        'pack_cost': pack_cost,
                        'final_count': get_whole(material['final_count'], f'Material {i} units per finished item'),
                    })
                total_cost = calculate_costs(products, final_amount)
                revenue = money(price * final_amount)
                result = {
                    'products': products,
                    'final_amount': final_amount,
                    'total_cost': total_cost,
                    'revenue': revenue,
                    'profit': money(revenue - total_cost),
                }
            except ValueError as exc:
                error = str(exc)

    return render_template('index.html', form=form, result=result, error=error)


if __name__ == '__main__':
    app.run(debug=True)
