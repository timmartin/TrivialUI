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
           pass
