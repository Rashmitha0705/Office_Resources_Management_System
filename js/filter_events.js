$(document).ready(function() {
    // Initialize datepicker plugin for date inputs
    $('input[type="date"]').datepicker();
  
    // Handle form submission
    $('#filter-form').on('submit', function(event) {
      event.preventDefault();
  
      // Get selected room and month
      const room = $('#room-select').val();
      const month = $('#month-select').val();
  
      // Send AJAX request to server
      $.ajax({
        url: '/filter_events',
        type: 'POST',
        data: {
          room: room,
          month: month
        },
        success: function(response) {
          // Clear existing table rows
          $('#events-table tbody tr').remove();
  
          // Add new rows to table
          response.forEach(function(event) {
            const start = new Date(event.start_time).toLocaleString();
            const end = new Date(event.end_time).toLocaleString();
            const title = event.title;
            const content = event.content;
  
            const row = $('<tr>');
            row.append($('<td>').text(start));
            row.append($('<td>').text(end));
            row.append($('<td>').text(title));
            row.append($('<td>').text(content));
  
            $('#events-table tbody').append(row);
          });
        },
        error: function() {
          alert('Error occurred while fetching events.');
        }
      });
    });
  });
$(document).ready(function() {
  // Initialize datepicker plugin for date inputs
  $('input[type="date"]').datepicker();

  // Handle form submission
  $('#filter-form').on('submit', function(event) {
    event.preventDefault();

    // Get selected room and month
    const room = $('#room-select').val();
    const month = $('#month-select').val();

    // Send AJAX request to server
    $.ajax({
      url: '/filter_events',
      type: 'POST',
      data: {
        room: room,
        month: month
      },
      success: function(response) {
        // Clear existing table rows
        $('#events-table tbody tr').remove();

        // Add new rows to table
        response.forEach(function(event) {
          const start = new Date(event.start_time).toLocaleString();
          const end = new Date(event.end_time).toLocaleString();
          const title = event.title;
          const content = event.content;

          const row = $('<tr>');
          row.append($('<td>').text(start));
          row.append($('<td>').text(end));
          row.append($('<td>').text(title));
          row.append($('<td>').text(content));

          $('#events-table tbody').append(row);
        });
      },
      error: function() {
        alert('Error occurred while fetching events.');
      }
    });
  });
});
v  