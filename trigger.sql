use OSS

go

create trigger delete_shop on shop after update
as
if exists(select * from inserted where is_valid=0)
begin
update goods set is_valid = 0 where shop_id in (select inserted.shop_id from inserted where inserted.is_valid=0) ;
update goods_order set is_valid = 0 where shop_id in (select inserted.shop_id from inserted where inserted.is_valid=0) ;
update favorite_shops set is_valid = 0 where shop_id in (select inserted.shop_id from inserted where inserted.is_valid=0);
end
go

create trigger deal_transaction on transaction_inf after update
as
if exists((select* from inserted where transaction_status='已通过' and transaction_type='开店申请') union (select* from inserted where transaction_status='已拒绝' and transaction_type='开店申请'))
begin
update shop set apply_status = '已通过' where user_id in (select user_id from inserted where transaction_status='已通过' and transaction_type='开店申请')
update shop set apply_status = '未通过' where user_id in (select user_id from inserted where transaction_status='已拒绝' and transaction_type='开店申请')
end
go

create trigger delete_user on user_inf after update
as
if exists(select* from inserted where is_valid=0)
begin
update goods_order set is_valid = 0 where user_id in (select user_id from inserted where is_valid=0) ;
update favorite_shops set is_valid = 0 where user_id in (select user_id from inserted where is_valid=0);
update receiver set is_valid = 0 where user_id in (select user_id from inserted where is_valid=0) ;
update transaction_inf set is_valid = 0 where user_id in (select user_id from inserted where is_valid=0) ;
update favorite_goods set is_valid = 0 where user_id in (select user_id from inserted where is_valid=0);
update shop set is_valid = 0 where user_id in (select user_id from inserted where is_valid=0) ;
update shopping_cart set is_valid = 0 where user_id in (select user_id from inserted where is_valid=0) ;
end
go

create trigger delete_goods on goods after update
as
if exists(select* from inserted where is_valid=0)
begin
update favorite_goods set is_valid = 0 where goods_id in (select goods_id from inserted where is_valid=0);
update goods_attribute set is_valid = 0 where goods_id in (select goods_id from inserted where is_valid=0);
update shopping_cart set is_valid = 0 where goods_id in (select goods_id from inserted where is_valid=0);
update goods_image set is_valid = 0 where goods_id in (select goods_id from inserted where is_valid=0);
end
go

create trigger create_order on goods_in_order after insert
as
declare @atr_id int,@good_num int
declare cur cursor for (select attribute_id,goods_num from inserted)
open cur
fetch next from cur into @atr_id,@good_num
while @@FETCH_STATUS=0
begin
	if @good_num>(select inventory from goods_attribute where attribute_id=@atr_id)
	begin
		raiserror('购买数量多于库存',16,1)
		rollback
	end
	else
	begin
		update goods_attribute set inventory=inventory-@good_num where attribute_id=@atr_id
	end
fetch next from cur into @atr_id,@good_num
end
close cur
deallocate cur
go



create trigger pay_order on goods_order after update
as
if exists(select * from inserted,deleted where inserted.order_id=deleted.order_id and inserted.order_status='待发货' and deleted.order_status<>'待支付')
begin
	update receiver set used_times = used_times + 1 where receiver_id in (select inserted.receiver_id from inserted,deleted where inserted.order_id=deleted.order_id and inserted.order_status='待发货' and deleted.order_status='待支付')
	declare @g_id int,@g_num int;
	declare cur1 cursor for (select goods_id, goods_num from goods_in_order where order_id in (select inserted.order_id from inserted,deleted where inserted.order_id=deleted.order_id and inserted.order_status='待发货' and deleted.order_status='待支付'))
	open cur1
	fetch next from cur1 into @g_id,@g_num
	while @@FETCH_STATUS=0
	begin
		update goods set sales = sales + @g_num where goods_id = @g_id;
		fetch next from cur1 into @g_id,@g_num
	end
	close cur1
	deallocate cur1
end
go

create trigger cancel_order on goods_order after update
as
if exists(select* from inserted,deleted where inserted.order_id=deleted.order_id and deleted.order_status='待支付' and inserted.order_status='已取消')
begin
	declare @atr_id int,@goods_num int
	declare cur2 cursor for (select attribute_id,goods_num from goods_in_order where order_id in (select inserted.order_id from inserted,deleted where inserted.order_id=deleted.order_id and deleted.order_status='待支付' and inserted.order_status='已取消'))
	open cur2
	fetch next from cur2 into @atr_id,@goods_num
	while @@FETCH_STATUS=0
	begin
		update goods_attribute set inventory=inventory+@goods_num where attribute_id=@atr_id
		fetch next from cur2 into @atr_id,@goods_num
	end
	close cur2
	deallocate cur2
	delete from goods_in_order where order_id in (select inserted.order_id from inserted,deleted where inserted.order_id=deleted.order_id and deleted.order_status='待支付' and inserted.order_status='已取消')
end
go





