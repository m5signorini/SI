/*create or replace function to_char_immutable(orderdate date)
    returns text as
    $$
        select to_char(orderdate, 'YYYYMM');
    $$
    language sql
    IMMUTABLE;

drop index idx_customers_creditcartype;
create index idx_customers_creditcartype on customers(creditcardtype);
drop index idx_orders_customerid_orderdate;
create index idx_orders_customerid_orderdate on orders(customerid,to_char_immutable(orders.orderdate));
explain select count(distinct(customers.city))
from customers
    join orders on customers.customerid = orders.customerid
where to_char_immutable(orders.orderdate) = '201604'
    and customers.creditcardtype = 'VISA';
*/

/*explain select customerid
from customers
where customerid not in (
 select customerid
 from orders
 where status='Paid'
);

explain select customerid
from (
 select customerid
 from customers
 union all
 select customerid
 from orders
 where status='Paid'
) as A
group by customerid
having count(*) =1;

explain select customerid
from customers
except
 select customerid
 from orders
 where status='Paid';*/

 drop index idx_orders_status;
 analyze orders;


 -- Exampl 1
 explain select count(*)
 from orders
 where status is null;


 --Example 2
 explain select count(*)
 from orders
 where status ='Shipped';
