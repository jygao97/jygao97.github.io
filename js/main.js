// Dean Attali / Beautiful Jekyll 2016

var main = {

  bigImgEl : null,
  numImgs : null,

  init : function() {
    main.initSectionNavigation();

    // On mobile, hide the avatar when expanding the navbar menu
    $('#main-navbar').on('show.bs.collapse', function () {
      $(".navbar").addClass("top-nav-expanded");
    });
    $('#main-navbar').on('hidden.bs.collapse', function () {
      $(".navbar").removeClass("top-nav-expanded");
    });

    // Close the mobile menu after following an in-page section link.
    // Wait for collapse before focusing so the fixed menu cannot cover the heading.
    $('#main-navbar').on('click', 'a[href^="#"]', function() {
      var target = document.getElementById(this.hash.slice(1));
      var navbar = $('#main-navbar');
      if (target && navbar.hasClass('in')) {
        navbar.one('hidden.bs.collapse', function() {
          target.focus({ preventScroll: true });
          target.scrollIntoView();
        });
        navbar.collapse('hide');
      }
    });

    // On mobile, when clicking on a multi-level navbar menu, show the child links
    $('#main-navbar').on("click", ".navlinks-parent", function(e) {
      var target = e.target;
      $.each($(".navlinks-parent"), function(key, value) {
        if (value == target) {
          $(value).parent().toggleClass("show-children");
        } else {
          $(value).parent().removeClass("show-children");
        }
      });
    });

    // Ensure nested navbar menus are not longer than the menu header
    var menus = $(".navlinks-container");
    if (menus.length > 0) {
      var navbar = $("#main-navbar ul");
      var fakeMenuHtml = "<li class='fake-menu' style='display:none;'><a></a></li>";
      navbar.append(fakeMenuHtml);
      var fakeMenu = $(".fake-menu");

      $.each(menus, function(i) {
        var parent = $(menus[i]).find(".navlinks-parent");
        var children = $(menus[i]).find(".navlinks-children a");
        var words = [];
        $.each(children, function(idx, el) { words = words.concat($(el).text().trim().split(/\s+/)); });
        var maxwidth = 0;
        $.each(words, function(id, word) {
          fakeMenu.html("<a>" + word + "</a>");
          var width =  fakeMenu.width();
          if (width > maxwidth) {
            maxwidth = width;
          }
        });
        $(menus[i]).css('min-width', maxwidth + 'px')
      });

      fakeMenu.remove();
    }

    // show the big header image
    main.initImgs();
  },

  initSectionNavigation : function() {
    var profile = document.querySelector('.profile-page');
    if (!profile) {
      return;
    }

    var sections = [];
    var links = document.querySelectorAll('#main-navbar a[href^="#"]');
    for (var i = 0; i < links.length; i++) {
      var heading = document.getElementById(links[i].hash.slice(1));
      if (heading) {
        sections.push({ link: links[i], heading: heading });
      }
    }
    if (!sections.length) {
      return;
    }

    var pending = false;
    var update = function() {
      pending = false;
      var current = sections[0];
      sections.forEach(function(section) {
        var offset = parseFloat(window.getComputedStyle(section.heading).scrollMarginTop) || 80;
        if (section.heading.getBoundingClientRect().top <= offset + 2) {
          current = section;
        }
      });

      // The last section can be shorter than the viewport.
      if (window.pageYOffset > 0 &&
          window.pageYOffset + window.innerHeight >= document.documentElement.scrollHeight - 2) {
        current = sections[sections.length - 1];
      }
      sections.forEach(function(section) {
        if (section === current) {
          section.link.setAttribute('aria-current', 'location');
        } else {
          section.link.removeAttribute('aria-current');
        }
      });
    };
    var schedule = function() {
      if (!pending) {
        pending = true;
        window.requestAnimationFrame(update);
      }
    };

    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
    window.addEventListener('hashchange', schedule);
    window.addEventListener('pageshow', schedule);
    window.addEventListener('load', schedule);
    if (window.ResizeObserver) {
      // Opening author lists or internships can move the section boundaries.
      new ResizeObserver(schedule).observe(profile);
    }
    update();
  },

  initImgs : function() {
    // If the page was large images to randomly select from, choose an image
    if ($("#header-big-imgs").length > 0) {
      main.bigImgEl = $("#header-big-imgs");
      main.numImgs = main.bigImgEl.attr("data-num-img");

          // 2fc73a3a967e97599c9763d05e564189
	  // set an initial image
	  var imgInfo = main.getImgInfo();
	  var src = imgInfo.src;
	  var desc = imgInfo.desc;
  	  main.setImg(src, desc);

	  // For better UX, prefetch the next image so that it will already be loaded when we want to show it
  	  var getNextImg = function() {
	    var imgInfo = main.getImgInfo();
	    var src = imgInfo.src;
	    var desc = imgInfo.desc;

		var prefetchImg = new Image();
  		prefetchImg.src = src;
		// if I want to do something once the image is ready: `prefetchImg.onload = function(){}`

  		setTimeout(function(){
                  var img = $("<div></div>").addClass("big-img-transition").css("background-image", 'url(' + src + ')');
  		  $(".intro-header.big-img").prepend(img);
  		  setTimeout(function(){ img.css("opacity", "1"); }, 50);

		  // after the animation of fading in the new image is done, prefetch the next one
  		  //img.one("transitioned webkitTransitionEnd oTransitionEnd MSTransitionEnd", function(){
		  setTimeout(function() {
		    main.setImg(src, desc);
			img.remove();
  			getNextImg();
		  }, 1000);
  		  //});
  		}, 6000);
  	  };

	  // If there are multiple images, cycle through them
	  if (main.numImgs > 1) {
  	    getNextImg();
	  }
    }
  },

  getImgInfo : function() {
  	var randNum = Math.floor((Math.random() * main.numImgs) + 1);
    var src = main.bigImgEl.attr("data-img-src-" + randNum);
	var desc = main.bigImgEl.attr("data-img-desc-" + randNum);

	return {
	  src : src,
	  desc : desc
	}
  },

  setImg : function(src, desc) {
	$(".intro-header.big-img").css("background-image", 'url(' + src + ')');
	if (typeof desc !== typeof undefined && desc !== false) {
	  $(".img-desc").text(desc).show();
	} else {
	  $(".img-desc").hide();
	}
  }
};

// 2fc73a3a967e97599c9763d05e564189

document.addEventListener('DOMContentLoaded', main.init);
