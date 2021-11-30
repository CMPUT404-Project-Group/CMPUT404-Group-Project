<h1> Description </h1>

The frontend of this application is contained within the `app/` directory, and is created and managed with default Django function and class based views and html template files. There are no migrations or models associated with the frontend. Its primary responsibilty is to make requests and render the responses, accessing our local data through our [api](https://social-distribution-t10.herokuapp.com/api/swagger/), and remote data through the `requests` library or `ajax`.

<h1> Available Routes/Pages </h1>

All routes will be prefixed with our heroku domain: `https://social-distribution-t10.herokuapp.com/app`

| route                                  | description                                                                                                                                                                    |
| :------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `/`                                    | Displays the logged in user's stream                                                                                                                                           |
| `/register`                            | Displays registration form, and registers user on submission. Depending on the site settings, the user may or may not be set to active and logged in.                          |
| `/accounts/login`                      | Displays the login form, and logs the user in if valid credentials are provided.                                                                                               |
| `create-post/`                         | Allows the user to create a new post. If the post is private to another user, it sends a POST ajax request to the users inbox.                                                 |
| `/posts/edit-post/<str:post_id>/`      | Allows the author to edit the contents of their post, specified by `<post_id>`.                                                                                                |
| `/posts/delete-post/<str:post_id>/`    | Allows the user to delete their post, specified by `<post_id>`.                                                                                                                |
| `/posts/<str:post_id>/`                | Allows the user to view the post, specified by `<post_id>`.                                                                                                                    |
| `/posts/view/foreign-post/`            | Allows user to view a foreign post (from another server).                                                                                                                      |
| `/posts/<str:post_id>/create-comment/` | Allows user to create a comment on the post specified by `<post_id>`.                                                                                                          |
| `/posts/<str:post_id>/comments/`       | Allows user to view the comments of the post specified by `<post_id>`.                                                                                                         |
| `/profile/`                            | Allows the user to view their profile.                                                                                                                                         |
| `/profile/followers/`                  | Allows the user to view all of their followers.                                                                                                                                |
| `/profile/manage/`                     | Allows the user to manage and edit their profile.                                                                                                                              |
| `/profile/<str:other_user_id>/`        | Allows the user to view another user's profile, specified by `<other_user_id>`.                                                                                                |
| `/posts/share-post/<str:post_id>/`     | Allows the user to share the post post specified by `<post_id>`.                                                                                                               |
| `follow/<str:other_user_id>/`          | Allows the user to send a friend request and follow another user, specified by `<other_user_id>`. It sends a friend request to the other user's inbox with a POST ajax request |
| `/unfollow/<str:other_user_id>`        | Allows the user to unfollow another, specified by `<other_user_id>`.                                                                                                           |
| `/author/<str:author_id>/inbox/`       | Allows the user to view and manage their inbox. To clear the inbox, and ajax DELETE request is sent to the API.                                                                |
| `/posts/`                              | Allows user to view all public posts (local and foreign).                                                                                                                      |
| `/authors/`                            | Allows user to view alll authors (local and foreign).                                                                                                                          |
