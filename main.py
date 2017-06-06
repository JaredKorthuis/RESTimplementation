#!/usr/bin/env python

from google.appengine.ext import ndb
import json
import webapp2

class Customer(ndb.Model):
    name = ndb.StringProperty()
    balance = ndb.FloatProperty()
    checked_out = ndb.StringProperty(repeated=True)

class Book(ndb.Model):
    title = ndb.StringProperty()
    isbn = ndb.StringProperty()
    genre = ndb.StringProperty(repeated=True)
    author = ndb.StringProperty()
    checkedIn = ndb.BooleanProperty()

    @classmethod
    def query_book(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.isbn)

class BookHandler(webapp2.RequestHandler):

    # Adding books
    def post(self):
        book_parent_key = ndb.Key(Book, "parent_book")
        book_data = json.loads(self.request.body)
        new_book = Book(parent=book_parent_key, 
                        title=book_data['title'], 
                        isbn=book_data['isbn'], 
                        genre=book_data['genre'], 
                        author=book_data['author'], 
                        checkedIn=book_data['checkedIn'])
        new_book.put()
        book_dict = new_book.to_dict()
        book_dict['self'] = '/books/' + new_book.key.urlsafe()
        book_dict['id'] = new_book.key.urlsafe()
        self.response.write(json.dumps(book_dict))

    def get(self, id=None):
        if id:
            b = ndb.Key(urlsafe=id).get()
            b.put()
            b_d = b.to_dict()
            b_d['self'] = "/books/" + id
            self.response.write(json.dumps(b_d))
            
        # Getting the books in the library
        else:
            if "checkedIn" in self.request.query_string:
                status_log = self.request.get("checkedIn")
                allbooks = Book.query()
                checked_books = []
                if status_log == 'false':
                    books = allbooks.filter(Book.checkedIn==False).fetch()
                else:
                    books = allbooks.filter(Book.checkedIn==True).fetch()
                
                for i in books:
                    checked_books.append(i.title)
                self.response.write(json.dumps(checked_books))
            else:
                qry = Book.query().fetch()
                myList = []
                for i in qry:
                    myList.append(i.to_dict())
                self.response.write(json.dumps(myList))

    def delete(self, id=None):
        if id:
            b = ndb.Key(urlsafe=id).get()
            b.key.delete()

class CheckOutHandler(webapp2.RequestHandler):
    def get(self, id=None):
        if id:
            c = ndb.Key(urlsafe=id).get()
            c.put()
            c_o = c.to_dict()
            c_o['self'] = "/customers/(.*)/books/(.*)"+id
            self.response.write(json.dumps(c_o))
        else:
            print "stuff"

class CustomerHandler(webapp2.RequestHandler):
    def post(self):
        customer_parent_key = ndb.Key(Customer, "parent_customer")
        customer_data = json.loads(self.request.body)
        new_customer = Customer(parent=customer_parent_key,
                                name=customer_data['name'],
                                balance=customer_data['balance'],
                                checked_out=customer_data['checked_out'])
        new_customer.put()
        customer_dict = new_customer.to_dict()
        customer_dict['self'] = '/customers/' + new_customer.key.urlsafe()
        customer_dict['id'] = new_customer.key.urlsafe()
        self.response.write(json.dumps(customer_dict))

    def get(self, mah_customer =None, mah_book=None):
        if mah_book:
            select = ndb.Key(urlsafe=mah_customer).get()
            select.put()
            selected = select.to_dict()
            selected['id'] = mah_book
            self.response.write(json.dumps(selected))
        elif mah_customer:
            c = ndb.Key(urlsafe=mah_customer).get()
            c.put()
            c_d = c.to_dict()
            c_d['self'] = "/customers/" + mah_customer
            self.response.write(json.dumps(c_d))
        else:
            qry = Customer.query().fetch()
            List = []
            for i in qry:
                List.append(i.to_dict())
            self.response.write(json.dumps(List))
    
    def delete(self, mah_customer=None, mah_book=None):
        customer = ndb.Key(urlsafe=mah_customer).get()
        book = ndb.Key(urlsafe=mah_book).get()
        customer.checked_out.remove("/books/"+str(mah_book))
        customer.put()
        book.checkedIn = True
        book.put()
            
            
    def put(self, mah_customer=None, mah_book=None):
            customer = ndb.Key(urlsafe=mah_customer).get()
            book = ndb.Key(urlsafe=mah_book).get()
            
            customer.checked_out.append("/books/"+str(mah_book))
            customer.put()
            
            book.checkedIn = False
            book.put()
class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write("Hello")

    # Deletes everything from root
    def delete(self):
        book = Book.query().fetch()
        customer = Customer.query().fetch()

        list_of_keys_book = ndb.put_multi(book)
        ndb.delete_multi(list_of_keys_book)

        list_of_keys_customer = ndb.put_multi(customer)
        ndb.delete_multi(list_of_keys_customer)


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/books', BookHandler),
    ('/books/(.*)', BookHandler),
    ('books?checkedIn=false',BookHandler),
    ('/customers', CustomerHandler),
    ('/customers/(.*)/books/(.*)', CustomerHandler),
    ('/customers/(.*)', CustomerHandler)
], debug=True)
