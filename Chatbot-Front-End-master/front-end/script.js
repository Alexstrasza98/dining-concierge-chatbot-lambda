var apigClient = apigClientFactory.newClient({});

// test code
// var body = {
//   message: 'sadsad'
// };
// var res = apigClient
//   .chatbotPost({}, body, {})
//   .then(function(result) {
//     console.log(result.data.body);
//   })
//   .catch(function(result) {
//     // Add error callback code here.
//   });

var $messages = $('.messages-content'),
  d,
  h,
  m,
  i = 0;

$(window).load(function() {
  $messages.mCustomScrollbar();
  setTimeout(function() {
    sendMessage('Hi~');
  }, 100);
});

function updateScrollbar() {
  $messages.mCustomScrollbar('update').mCustomScrollbar('scrollTo', 'bottom', {
    scrollInertia: 10,
    timeout: 0
  });
}

function setDate() {
  d = new Date();
  if (m != d.getMinutes()) {
    m = d.getMinutes();
    $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo(
      $('.message:last')
    );
  }
}
function postMessage(msg) {
  var body = {
    message: msg
  };
  apigClient
    .chatbotPost({}, body, {})
    .then(function(result) {
      console.log('posting');
      // var res = JSON.parse(result.data.body).message;
      var res = result.data.body;
      console.log(res);
      sendMessage(res);
    })
    .catch(function(result) {
      sendMessage('please speak again.');
    });
}

function insertMessage() {
  msg = $('.message-input').val();
  if ($.trim(msg) == '') {
    return false;
  }
  $('<div class="message message-personal">' + msg + '</div>')
    .appendTo($('.mCSB_container'))
    .addClass('new');
  setDate();
  $('.message-input').val(null);
  updateScrollbar();
  setTimeout(function() {
    postMessage(msg);
  }, 1000);
}

$('.message-submit').click(function() {
  insertMessage();
});

$(window).on('keydown', function(e) {
  if (e.which == 13) {
    insertMessage();
    return false;
  }
});

function sendMessage(msg) {
  if ($('.message-input').val() != '') {
    return false;
  }
  $(
    '<div class="message loading new"><figure class="avatar"><img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/156381/profile/profile-80_4.jpg" /></figure><span></span></div>'
  ).appendTo($('.mCSB_container'));
  updateScrollbar();

  setTimeout(function() {
    $('.message.loading').remove();
    $(
      '<div class="message new"><figure class="avatar"><img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/156381/profile/profile-80_4.jpg" /></figure>' +
        msg +
        '</div>'
    )
      .appendTo($('.mCSB_container'))
      .addClass('new');
    setDate();
    updateScrollbar();
  }, 1000);
}
