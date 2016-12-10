Examples
========

Application main function
-------------------------

If you want to get anything to display, you'll need to start an
application like this:

.. code::

   import TrivialUI

   if __name__ == '__main__':
       with TrivialUI.Application() as app:
           # Create your windows here...
           pass


Simple dashboard
----------------

To have a dashboard with some buttons:

.. code::

   def yo():
       print "yo"

   class Dashboard(TrivialUI.MainWindow):
       widgets = [
           TrivialUI.Button("Yo", on_click=yo)
       ]

       def __init__(self):
           super(Dashboard, self).__init__(title='Dashboard')


Start the application like this:

.. code::

   with TrivialUI.Application():
       window = Dashboard()
       window.show()

The `on_click` of the button takes an ordinary Python callable.
