-- To add to the index the date criteria, we have to create an IMMUTABLE function. to_char cannot be used, as it isn't immutable, to define an Index

create or replace function to_char_immutable(orderdate date)
    returns text as
    $$
        select to_char(orderdate, 'YYYYMM');
    $$
    language sql
    IMMUTABLE;

-- c) and e) Index to increase the query performance
-- We create an index based on the credit card type of a certain customer because it's one of searching criteria of the query
drop index idx_customers_creditcartype;
create index idx_customers_creditcartype on customers(creditcardtype);
-- We can also create one based on the date, formatted
drop index idx_orders_orderdate;
create index idx_orders_orderdate on orders(to_char_immutable(orders.orderdate));
-- We try to create both previous indexes at the same time and try how it improves the query performance
drop index idx_orders_orderdate;
create index idx_orders_orderdate on orders(to_char_immutable(orders.orderdate));

drop index idx_customers_creditcartype;
create index idx_customers_creditcartype on customers(creditcardtype);
-- We create an index based on the customerid to see how it may not have any result at all
-- psql create by default implicit indexes based on the primary key of every table.
drop index idx_customers_customerid;
create index idx_customers_customerid on customers(customerid);
-- We create an index in orders for customerid to see how it affects the performance, since this attribute of orders is used as
-- the join on condition in the query
drop index idx_orders_customerid;
create index idx_orders_customerid on orders(customerid);
-- We will try now with an index that is a tuple and see the results of the explain consult
drop index idx_orders_customerid_orderdate;
create index idx_orders_customerid_orderdate on orders(customerid,to_char_immutable(orders.orderdate));
-- To finish we try with this last compound index and also with the creditcardtype one
drop index idx_customers_creditcartype;
create index idx_customers_creditcartype on customers(creditcardtype);
drop index idx_orders_customerid_orderdate;
create index idx_orders_customerid_orderdate on orders(customerid,to_char_immutable(orders.orderdate));


-- a) Consulta
select count(distinct(customers.city))
from customers
    join orders on customers.customerid = orders.customerid
where to_char_immutable(orders.orderdate) = '201604'
    and customers.creditcardtype = 'VISA';

-- b) Explain
explain select count(distinct(customers.city))
from customers
    join orders on customers.customerid = orders.customerid
where to_char_immutable(orders.orderdate) = '201604'
    and customers.creditcardtype = 'VISA';
