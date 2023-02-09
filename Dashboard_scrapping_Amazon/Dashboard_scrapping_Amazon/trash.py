products_dict = products.to_dict('records')
    iterate = 0
    for row in products_dict:
        iterate += 1
        stars_list = []
        for i in range(row['rating']):
            stars_list.append(html.li(html.I(className="fa fa-star"), className="list-inline-item"))
        for i in range(5-row['rating']):
            stars_list.append(html.li(html.I(className="fa fa-star-o"), className="list-inline-item"))

        product_item = \
            dbc.Col(html.Div(
                [
                    html.Div(html.Img(src="/static/images/Amazon-logo.png", className="img-fluid", width="150px"),
                             className="img-box"),
                    html.Div(
                        [
                            html.H4("product title"),
                            html.P(html.Span("product price"), className="item-price"),
                            html.Div(html.Ul([], className="list-inline"), className="star-rating")
                        ],
                        className="thumb-content")
                ],
                className="thumb-wrapper"
            ),
                width=3)


# show products
    products_list = []
    for index, row in products.iterrows():
        img = row['img']
        title = (row['title'][:80] + '..') if len(row['title']) > 80 else row['title']
        price = row['price']

        rating = []
        for i in range(int(row['rating'])):
            rating.append(html.I(className="fas fa-star"))
        for j in range(5 - int(row['rating'])):
            rating.append(html.I(className="far fa-star"))

        product_item = dbc.Col(
            dbc.Card(
                [
                    html.A(dbc.CardImg(src=img, className="product-img"), href="#"),
                    dbc.CardBody(
                        [
                            html.A(html.H6(title), className="product-title", href="#"),
                            html.H3('$' + str(price)),
                            html.Div(rating, className="text-warning")
                        ],
                        className="text-center"
                    ),

                ],
                className=" border-0"
            ),
            width=3,
            className="product-item"

        )

        products_list.append(product_item)


# function for grouped list
def grouped(iterable, n):
    return zip(*[iter(iterable)] * n)
