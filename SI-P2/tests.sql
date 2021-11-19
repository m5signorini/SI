select * from products join alerts on alerts.inventoryid = inventory.inventoryid
    join inventory on inventory.prod_id = products.prod_id
    where prod_id = 10;
