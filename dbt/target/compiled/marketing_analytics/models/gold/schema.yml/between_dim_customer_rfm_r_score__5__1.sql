
select * from "marketing"."gold"."dim_customer_rfm"
where r_score is not null
  and (r_score < 1 or r_score > 5)
