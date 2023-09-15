# from django.test import TestCase
# from rest_framework.test import APIClient

# class AddPostTestCase(TestCase):

#     def setUp(self):
#         self.client = APIClient()

#     def test_add_post(self):
#         data = {
#             # Provide necessary data for the post
#             'user': {
#                 'user_id': 1
#             },
#             'post_city': 'New York',
#             'post_street': 'Main Street',
#             # Add other required fields...
#         }

#         response = self.client.post('/add_post/', data, format='json')

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data, "Post successfully saved in db")

#     def test_add_post_invalid_data(self):
#         data = {
#             # Missing required data...
#         }

#         response = self.client.post('/add_post/', data, format='json')

#         self.assertEqual(response.status_code, 500)
#         self.assertIn("Post validation failed", str(response.content))
