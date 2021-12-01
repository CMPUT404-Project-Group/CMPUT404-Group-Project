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

<h1>Server Administration</h1>
Server administration functions are handled through the default django administration site. From here, server-admins can create, edit, and delete:

- users
- user friendships
- posts
- nodes
- authentication tokens (for nodes)

<h2> Adding and Connecting Nodes </h2>

To add a new node to connect to, server-admins simply have to add a new node through the administration site. They can enter the _Team_ name, _url_ to their serivce, and the _authentication token_ provided by the other server. Nodes can be toggled as active or inactive with the _is_active_ option. If the node is set to `is_active=False`, the server will not make any requests to that server and will not collect any of their data (users, posts, etc).

<h2> Authenticating Nodes </h2>

To allow other nodes to connect to the server requires three steps:

1. Create a new user with `type=NODE` and `is_active=True`. The remaining fields can be set to anything.
2. Create a new Auth Token for the user created in step 1.
3. Provide the remote server with the token generaetd in step 2.

To disable a remote node from connecting, we can simply change `is_active=False` for the desired node. They can be reactivated at any time by changing `is_active=True`.
