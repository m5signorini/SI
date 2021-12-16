-- To add to the index the date criteria, we have to create an IMMUTABLE function. to_char cannot be used, as it isn't immutable, to define an Index

create or replace function to_char_immutable(orderdate date)
    returns text as
    $$
        select to_char(orderdate, 'YYYYMM');
    $$
    language sql
    IMMUTABLE;

-- c) Index to increase the query performance
-- We create an index based on the credit card type of a certain customer because it's one of searching criteria of the query
drop index idx_customers_creditcartype
create index idx_customers_creditcartype on customers(creditcardtype)
-- We can also create one based on the date, formatted
drop index idx_orders_orderdate
create index idx_orders_orderdate on orders(to_char_immutable(orderdate))

-- a) Consulta
select count(distinct(customers.city))
from customers
    join orders on customers.customerid = orders.customerid
where to_char(orders.orderdate, 'YYYYMM') = '201604'
    and customers.creditcardtype = 'VISA';

-- b) Explain
explain select count(distinct(customers.city))
from customers
    join orders on customers.customerid = orders.customerid
where to_char(orders.orderdate, 'YYYYMM') = '201604'
    and customers.creditcardtype = 'VISA';
