insert into sequence(title) values ('Mort seq');
insert into book values (1,'Mort', 'Annotation. Must be a Huge annotation here.', 1, 1);
insert into book values (2,'Mortana', NULL, 1, 2);
insert into book values (3,'Lird', 'Realy big, big, huge annotation must be here. Hope it is big enough..', NULL, NULL);
insert into book values (
    4, 
    'Книга Титанов', 
    'Книга про великих Титанов. Убивали и грабили всех. Родился невзрачный мальчик, вырос, стал героем и всех порешал.',
    NULL,
    NULL
);
insert into author(first_name, last_name) values ('John', 'Doe');
insert into author(first_name, last_name) values ('Jane', 'Doe');
insert into author(first_name, last_name) values ('Вася', 'Пупкин');
insert into author_book values (1,1);
insert into author_book values (1,2);
insert into author_book values (2,3);
insert into author_book values (3,4);
insert into genre values (1, 'drama');
insert into genre values (2, 'crime');
insert into genre values (3, 'story');
insert into genre values (4, 'adventure');

insert into book_genre values (1, 1);
insert into book_genre values (1, 2);
insert into book_genre values (1, 3);
insert into book_genre values (1, 4);
insert into book_genre values (2, 4);
insert into book_genre values (4, 4);
