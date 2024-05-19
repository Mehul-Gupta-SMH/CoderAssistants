SELECT *
FROM categories
JOIN products ON categories.category_id = products.category_id
JOIN suppliers ON products.supplier_id = suppliers.supplier_id
JOIN orderdetails ON products.product_id = orderdetails.product_id
JOIN orders ON orderdetails.order_id = orders.order_id
JOIN customers ON orders.customer_id = customers.customer_id
JOIN customercustomerdemo ON customers.customer_id = customercustomerdemo.customer_id
JOIN customerdemographics ON customercustomerdemo.customer_type_id = customerdemographics.customer_type_id
JOIN employees ON orders.employee_id = employees.employee_id
JOIN employeeterritories ON employees.employee_id = employeeterritories.employee_id
JOIN territories ON employee_territories.territory_id = territories.territory_id
JOIN region ON territories.region_id = region.region_id
JOIN shippers ON orders.ship_via = shippers.shipper_id
JOIN usstates ON shippers.ship_country = usstates.state_id;
