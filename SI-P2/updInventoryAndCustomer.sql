CREATE OR REPLACE FUNCTION tr_update_inventory_customer() RETURNS trigger AS $$
        BEGIN

		IF (new.status = 'Paid') THEN
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
		END IF;

			return NEW;
        END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER UPD_INVENTORY_CUSTOMER AFTER INSERT OR UPDATE
ON orders FOR EACH ROW
EXECUTE PROCEDURE tr_update_inventory_customer();
