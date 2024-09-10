--задача 1 на нахождение города с минимальным населением
SELECT * FROM City 
WHERE population = (SELECT MIN(population) FROM City);

--задача 2 
SELECT COUNT(DISTINCT name) FROM myTable
where label like 'bot%'
group by ID

--задача 3
select sum(p.amount)/count(p.user_id) as arpu 
from payment as p
left join user_ as u
on p.user_id = u.user_id
where month(u.installed_at) = 1 and year(u.installed_at) = 2023
group by month(p.payment_at)