--QUERIES FOR INSERTING,UPDATING AND DELETING ORDERDETAIL
CREATE OR REPLACE FUNCTION tr_update_orders() RETURNS trigger AS $$
        BEGIN
			IF (TG_OP = 'INSERT') THEN
				IF EXISTS (
					SELECT * from inventory
					where inventory.prod_id = new.prod_id
						and stock < new.quantity
				) THEN
					RAISE EXCEPTION 'Not enough stock';
				END IF;

				UPDATE orders
				set netamount = netamount+(NEW.price),
							totalamount = (totalamount + ROUND(((NEW.price) * (1+tax/100))::numeric,2))::numeric
				where orders.orderid = new.orderid;
			ELSIF (TG_OP = 'UPDATE') THEN
				IF EXISTS (
					SELECT * from inventory
					where inventory.prod_id = new.prod_id
						and stock < new.quantity
				) THEN
					RAISE EXCEPTION 'Not enough stock';
				END IF;
				
				UPDATE orders
				set netamount = netamount+((NEW.price)-(OLD.price)),
							totalamount = (totalamount + ROUND((((NEW.price)-(OLD.price)) * (1+tax/100))::numeric,2))::numeric
				where orders.orderid = new.orderid;
			ELSE
				UPDATE orders
				set netamount = netamount-(OLD.price),
							totalamount = (totalamount- ROUND(((OLD.price) * (1+tax/100))::numeric,2))::numeric
				where orders.orderid = OLD.orderid;
			END IF;

			return NEW;
        END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER INS_ORDERDETAIL AFTER INSERT OR DELETE OR UPDATE
ON orderdetail FOR EACH ROW
EXECUTE PROCEDURE tr_update_orders();
