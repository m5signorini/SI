-- Exampl 1
select count(*)
from orders
where status is null;

--Example 2
select count(*)
from orders
where status ='Shipped';

-- Example 3
select count(*)
from orders
where status ='Paid';

-- Example 4
select count(*)
from orders
where status ='Processed';

-- Index to compare de results of the explain, with and without it
drop index idx_orders_status;
create index idx_orders_status on orders(status);

-- Llamada a la sentencia analyze
analyze orders;
