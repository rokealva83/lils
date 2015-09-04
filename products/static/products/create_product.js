    'use strict';

if(typeof PRODUCTS !== 'undefined') {

    var Product = Backbone.Model.extend({

    });

    var Products = Backbone.Collection.extend({
        model: Product,
    })

    var ProductSearchView = Backbone.View.extend({
        template: _.template($('#product-search').html()),

        tagName: 'div',
        className: 'row',

        events: {
            'input #barcode': 'onInput',
            'paste #barcode': 'onPaste',
        },

        initialize: function(options) {
            this.searchResultCollection = new Products();
            this.productsForSave = new Products();
            this.products = options.products;

            this.searchResultView = new ProductSerachResultView({
                products: this.searchResultCollection,
            });

            this.productTableView = new ProductTableView({
                products: this.productsForSave,
            });

            this.searchResultView.on('product:selected', this.productsForSave.add, this.productsForSave);
        },

        render: function() {
            this.$el.html(this.template());

            this.searchResultView.render();
            this.productTableView.render();

            this.$el.find('#search-result').append(this.searchResultView.$el);
            this.$el.find('#products-for-save').append(this.productTableView.$el);

            return this;
        },

        onPaste: function(e) {
            e.preventDefault();
            var pastedData = e.originalEvent.clipboardData.getData('text/plain').trim();
            $(e.target).val(pastedData);

            this.search(pastedData);
        },

        search: function(barcode) {
            var view = this;

            if(/^[0-9]*$/.test(barcode) && barcode.length) {
                $.get('/products/' + barcode + '/').success(function(searchResult) {
                        view.searchResultCollection.reset(searchResult)
                });
            }
        },

        onInput: function(e) {
            var barcode = $(e.target).val().trim();

            $(e.target).val(barcode);

            this.search(barcode);
        }
    });

    var ProductSerachResultView = Backbone.View.extend({
        template: _.template($('#product-search-result').html()),

        events: {
            'click .clickable': 'onItemClick',
        },

        initialize: function(options) {
            this.products = options.products;
            this.products.on('reset remove', this.onProductsReset, this);
        },

        render: function() {
            this.$el.html(this.template({
                products: this.products.toJSON()
            }));

            return this;
        },

        getQuantity: function(id) {
            return $('input[data-product-id=' + id + ']').val()
        },

        onProductsReset: function(products) {
            this.render();
        },

        onItemClick: function(e) {
            var row = $(e.target).parent();
            var product = this.products.get(row.data('productId'));

            product.set({
                quantity: this.getQuantity(product.get('id'))
            });

            this.products.remove(product);

            this.trigger('product:selected', product);
        }
    });

    var ProductTableView = Backbone.View.extend({
        template: _.template($('#product-table').html()),

        events: {
            'click #save': 'save'
        },

        initialize: function(options) {
            this.products = options.products;

            _.bind(this.save, this);

            this.products.on('add remove', this.onProductAdd, this);
        },

        save: function() {
            var requests = [],
                view = this;

            this.products.each(function(product) {
                requests.push(
                    $.post('', {
                        product: product.get('id'),
                        quantity_override: product.get('quantity'),
                    }).success(function() {
                        view.products.remove(product);
                    })
                );
            });

            $.when.apply($, requests).done(function() {
                console.log('all finished');
            })
        },

        render: function() {
            this.$el.html(this.template({
                products: this.products.toJSON()
            }));

            return this;
        },

        onProductAdd: function(product) {
            console.log(product)
            this.render();
        }
    });

    var products = new Products();

    var productSearchView = new ProductSearchView({
        el: '#container',
        products: products
    });

    productSearchView.render();

    window.products = products;
}
