
select * from "marketing"."gold"."dim_customer_rfm"
where f_score is not null
  and (f_score < 1 or f_score > 5)
