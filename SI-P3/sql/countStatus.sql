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

-- Explain of the two first examples without analyze and indexes
-- Exampl 1
explain select count(*)
from orders
where status is null;

--Example 2
explain select count(*)
from orders
where status ='Shipped';

-- Index to compare de results of the explain, with and without it
create index idx_orders_status on orders(status);

-- Exampl 1
explain select count(*)
from orders
where status is null;

--Example 2
explain select count(*)
from orders
where status ='Shipped';

drop index idx_orders_status;

-- Since this point every execution of explain will be different than usual, now we are giving extra information
-- in the form of statistics to the plannifier
analyze orders;

-- Explain of the two first examples without analyze and indexes
-- Exampl 1
explain select count(*)
from orders
where status is null;

--Example 2
explain select count(*)
from orders
where status ='Shipped';

-- Index to compare de results of the explain, with and without it
create index idx_orders_status on orders(status);

-- Exampl 1
explain select count(*)
from orders
where status is null;

--Example 2
explain select count(*)
from orders
where status ='Shipped';

drop index idx_orders_status;


-- Explain over the last two examples without indexes
-- Example 3
explain select count(*)
from orders
where status ='Paid';

-- Example 4
explain select count(*)
from orders
where status ='Processed';
-- Explain over the las two examples with index over the orders.status attribute
create index idx_orders_status on orders(status);

-- Example 3
explain select count(*)
from orders
where status ='Paid';

-- Example 4
explain select count(*)
from orders
where status ='Processed';

drop index idx_orders_status;
