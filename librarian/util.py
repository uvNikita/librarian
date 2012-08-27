# -*- coding: utf-8 -*-

from flask import request, url_for

from librarian.models import Book, Author


def current_url(save_get_params=False, **updates):
     kwargs = request.view_args.copy()
     if save_get_params:
         kwargs.update(request.args)
     kwargs.update(updates)
     return url_for(request.endpoint, **kwargs)


def books_sorted(query):
    return (
        query
        .order_by(Book.sequence_id)
        .order_by(Book.sequence_number)
    )


def authors_sorted(query):
    return (
        query
        .order_by(Author.last_name)
    )
