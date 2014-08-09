drop table if exists expenses;
create table expenses (
  id integer primary key autoincrement,
  date DATETIME not null,
  amount float not null,
  description text not null,
  category text not null
);
