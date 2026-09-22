// make sure all the images have loaded before starting any animation
$(window).on('load', function() {

  // just adding a little delay at the start to extend the 'loading' to see what is shown before the plugin is activated
  TweenLite.delayedCall(2, function() {
    // activate animation on the animatedimage elements
    $('.animatedimage').animateimage(5, -1)
    // setup a click on the box to toggle the animation pause
    .parent().on('click', function() {
      var image = $(this).children('.animatedimage');
      
      // the plugin saves the animation in the 'animation' property of the DOM element e.g. image[0].animation
      if (image.prop('animation').paused()) {
        image.prop('animation').resume();
      } else {
        image.prop('animation').pause();
      }
    });
  });
});



;(function($) {
  $.fn.animateimage = function(framerate, repeats) {
    return this.each(function() {

      var $this = $(this);
        
      framerate = Math.abs(framerate || 10);
      if (typeof repeats === 'undefined' || repeats < 0) repeats = 0;
      var duration = 1 / framerate;
      var spritesize = $this.data('spritesize');
      
      // grab all children of the target element - these should just be the image/s to animate
      var image = $this.children();
      

      if (spritesize) { // sprite sheet
        if (image.length === 1) { // image should be a single image containing the sprite sheet
          
          var horizontal = ($this.data('spritedirection') !== 'vertical');
          var spritecount = (horizontal ? image.width() : image.height()) / spritesize;
  
          TweenLite.set(image, { visibility: 'visible' });
          
          // attach a reference to the animation on the element, so it can be easily grabbed outside of the plugin and paused, reversed etc
          this.animation = new TimelineMax({ repeat: repeats });
  
          if (horizontal) {
            TweenLite.set(this, { width: spritesize });
            for (var i = 0; i < spritecount; i++) {
              this.animation.set(image, { left: "-" + (i*spritesize) + "px" }, i*duration);
            }
          } else {
            TweenLite.set(this, { height: spritesize });
            for (var i = 0; i < spritecount; i++) {
              this.animation.set(image, { top: "-" + (i*spritesize) + "px" }, i*duration);
            }
          }
          // add an 'empty' set after the last position change - this adds padding at the end of the timeline so the last frame is displayed for the correct duration before the repeat
          this.animation.set({}, {}, i*duration);
        }

      } else { // image sequence
        if (image.length > 1) { // image should only contain the images to be animated
          
          // styles for hidden and visible image in the sequcnce
          var hidden = { position: 'absolute', visibility: 'hidden' };
          var visible = { position: 'static', visibility: 'visible' };
    
          // in case the poster is not the first child, make sure its pre-animated state is disabled
          TweenLite.set(image.filter('.poster'), hidden);
    
          var lastimage = image.last();
          
          // attach a reference to the animation on the element, so it can be easily grabbed outside of the plugin and paused, reversed etc
          this.animation = new TimelineMax({ repeat: repeats })
              // this first set is not strictly needed as lastimage is underneath all of the other images, but it certainly doesn't hurt
              .set(lastimage, hidden)
              // toggle images one by one between visible and hidden - at any one time, only one image will be visible, and its static positioning will set the size for the container
              .staggerTo(image, 0, visible, duration, 0)
              // hide all the elements except lastimage - it will be hidden on repeat if needed at the same time as first is shown
              .staggerTo(image.not(lastimage), 0, $.extend(hidden, { immediateRender: false }), duration, duration)
              // add an 'empty' set after lastimage is made visible - this adds padding at the end of the timeline so lastimage is displayed for the correct duration before the repeat
              .set({}, {}, "+="+duration);
        }
        
      }
    });
  };
}(jQuery));