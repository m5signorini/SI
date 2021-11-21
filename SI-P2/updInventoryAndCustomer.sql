CREATE OR REPLACE FUNCTION tr_update_inventory_customer() RETURNS trigger AS $$
        BEGIN

		IF (new.status = 'Paid') THEN
			IF EXISTS (
				SELECT * from orderdetail
				join products on products.prod_id = orderdetail.prod_id 
					and orderdetail.orderid = old.orderid
				join inventory on products.prod_id = inventory.prod_id
				where stock < orderdetail.quantity
			) THEN
				RAISE EXCEPTION 'Not enough stock';
			END IF;

			UPDATE inventory as inv
			set stock = stock - orderdetail.quantity, sales = sales + orderdetail.quantity
			from (orders join orderdetail on orders.orderid = orderdetail.orderid)
			where orderdetail.orderid = old.orderid and orderdetail.prod_id = inv.prod_id;

			insert into alerts(empty_date, inventoryid)
			select NOW()::timestamp, orderdetail.prod_id
			from((orders join orderdetail on orders.orderid = orderdetail.orderid) join inventory on inventory.prod_id=orderdetail.prod_id)
			where orderdetail.orderid = old.orderid and inventory.stock = 0;

			update customers
			set balance = balance - new.totalamount, loyalty = loyalty + ((new.totalamount*100) * 0.05)
			from orders
			where orders.orderid = old.orderid and customers.customerid = old.customerid;

			insert into orders(orderid,orderdate, customerid, netamount, tax, totalamount)
			select orderid+1, NOW(),new.customerid,0,15,0
			from orders
			order by orderid desc
			limit 1;

		END IF;

		return NEW;
        END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER UPD_INVENTORY_CUSTOMER AFTER UPDATE
ON orders FOR EACH ROW
EXECUTE PROCEDURE tr_update_inventory_customer();
