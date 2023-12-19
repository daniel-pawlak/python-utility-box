# app.config['MAIL_USERNAME'] = 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
# import os
# my_variable = os.environ
# encoded_variable = os.environ.get('EMAIL_USER')
# print(my_variable,)

import os
# import pprint
  
# # Get the list of user's
# # environment variables
# env_var = os.environ
  
# # Print the list of user's
# # environment variables
# print("User's Environment variable:")
# pprint.pprint(dict(env_var), width = 1)

os.environ['EMAIL_USER'] = 'automationgwpl@gmail.com'
print(os.environ['EMAIL_USER'])