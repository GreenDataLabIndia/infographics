

slideshowApp = angular.module 'slideshowApp', []

# slideshowApp.config ($locationProvider)->
#   $locationProvider.html5Mode true

class SlideshowCtrl
  @$inject: ['$scope', '$http', '$sce', '$location']
  constructor: (@scope, @http, @sce, @location) ->
    @popup_active = ''
    @selected_year = {}
    @http.get('data/slideshow.json').success( (data)=>
      @data = data
      year = @location.search().year
      if year != undefined and @data[year] != undefined and @data[year].enabled == ""
        @selected_year = data[year]
      else
        @selected_year = data['1992']

    );

  selectYear: (year)->
    @data[@selected_year.year].is_active = ""
    @selected_year = @data[year]
    @data[year].is_active = "active"

  next: ()->
    if @selected_year.next > 0
      @selectYear(@selected_year.next)

  prev: ()->
    if @selected_year.prev > 0
      @selectYear(@selected_year.prev)

  togglePopup: ->
    if @popup_active == 'hide'
      @popup_active = ""
    else
      @popup_active = "hide"

  selectedGraphText: ->
    @sce.trustAsHtml @selected_year.graph_text

  getHtml: (text)->
    @sce.trustAsHtml text

  getThumbnail: ->
    if @popup_active != "hide" and @selected_year.year > 0
      return @selected_year.graph_thumbnail
    else
      return @selected_year.thumbnail

slideshowApp.controller 'SlideshowCtrl', SlideshowCtrl
