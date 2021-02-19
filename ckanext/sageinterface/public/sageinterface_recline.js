ckan.module('sageinterface_recline', function (jQuery) {
  return {
    options: {
        controlsClassName: "controls"
    },
    initialize: function () {
        jQuery.proxyAll(this, /_on/);
        this.options.resourceData = JSON.parse(this.options.resourceData);
        this.options.resourceView = JSON.parse(this.options.resourceView);
        this.el.ready(this._onReady);
    },
    _onReady: function() {
        var resourceData = this.options.resourceData,
            resourceView = this.options.resourceView;
  
        this.loadView(resourceData, resourceView);
    },
    loadView: function (resourceData, reclineView) {
        var self = this;
        function showError(msg){
          msg = msg || self._('error loading view');
          window.parent.ckan.pubsub.publish('data-viewer-error', msg);
        }
  
        var errorMsg, dataset, map_config;
        //console.log(resourceData);
        dataset = new recline.Model.Dataset({records: resourceData});
  
        var query = new recline.Model.Query();
        query.set({ size: reclineView.limit || 100 });
        query.set({ from: reclineView.offset || 0 });
  
        var urlFilters = {};
        try {
          if (window.parent.ckan.views && window.parent.ckan.views.filters) {
            urlFilters = window.parent.ckan.views.filters.get();
          }
        } catch(e) {}
        
        dataset.queryState.set(query.toJSON(), {silent: true});
  
        errorMsg = this._('Could not load view for sage interface');
        dataset.fetch()
          .done(function(dataset){
              self.initializeView(dataset);
          })
          .fail(function(error){
            if (error.message) errorMsg += ' (' + error.message + ')';
            showError(errorMsg);
          });
    },
    initializeView: function (dataset) {
        var view = this._newDataExplorer(dataset);
        view.visible = true;
        view.render();
    },
    _newDataExplorer: function (dataset) {
      var views = [
        {
          id: 'grid',
          label: this._('Grid'),
          view: new recline.View.SlickGrid({
            model: dataset
          })
        }
      ];

      var sidebarViews = [
        {
          id: 'valueFilter',
          label: this._('Filters'),
          view: new recline.View.ValueFilter({
            model: dataset
          })
        }
      ];

      var dataExplorer = new recline.View.MultiView({
        el: this.el,
        model: dataset,
        views: views,
        sidebarViews: sidebarViews,
        config: {
          readOnly: true
        }
      });

      return dataExplorer;
    },

    _renderControls: function (el, controls, className) {
        var controlsEl = jQuery("<div class=\"clearfix " + className + "\" />");
        for (var i = 0; i < controls.length; i++) {
          controlsEl.append(controls[i].el);
        }
        jQuery(el).append(controlsEl);
    }
  };
});
