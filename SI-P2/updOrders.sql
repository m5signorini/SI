--QUERIES FOR INSERTING,UPDATING AND DELETING ORDERDETAIL
CREATE OR REPLACE FUNCTION tr_update_orders() RETURNS trigger AS $$
        BEGIN
			IF (TG_OP = 'INSERT') THEN
				UPDATE orders
				set netamount = netamount+(NEW.price * NEW.quantity),
							totalamount = totalamount+((NEW.price * NEW.quantity)/tax+(NEW.price * NEW.quantity))
				where orders.orderid = new.orderid;
			ELSIF (TG_OP = 'UPDATE') THEN
				UPDATE orders
				set netamount = netamount+((NEW.price * NEW.quantity)-(OLD.price * OLD.quantity)),
							totalamount = totalamount+(((NEW.price * NEW.quantity)-(OLD.price * OLD.quantity))/tax+((NEW.price * NEW.quantity)-(OLD.price * OLD.quantity)))
				where orders.orderid = new.orderid;
			ELSE
				UPDATE orders
				set netamount = netamount-(OLD.price * OLD.quantity),
							totalamount = totalamount-((OLD.price * OLD.quantity)/tax+(OLD.price * OLD.quantity))
				where orders.orderid = OLD.orderid;
			END IF;

			return NEW;
        END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER INS_ORDERDETAIL AFTER INSERT OR DELETE OR UPDATE
ON orderdetail FOR EACH ROW
EXECUTE PROCEDURE tr_update_orders();
