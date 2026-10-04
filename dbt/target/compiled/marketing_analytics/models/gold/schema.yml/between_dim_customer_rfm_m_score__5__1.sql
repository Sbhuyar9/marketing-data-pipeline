
select * from "marketing"."gold"."dim_customer_rfm"
where m_score is not null
  and (m_score < 1 or m_score > 5)
