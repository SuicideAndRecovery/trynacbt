<?php
/**
 * Plugin Name: trynacbt
 */

function trynacbt_on_activation() {
  global $wpdb;

  /* Create tables. */
  $wpdb->query(
    "CREATE TABLE IF NOT EXISTS {$wpdb->prefix}trynacbt_threads (
      title VARCHAR(151)
      , datetimePosted VARCHAR(25)
      , uri VARCHAR(500)
      , UNiQUE KEY {$wpdb->prefix}idx_trynacbt_threads (uri)
    )"
  );
}
register_activation_hook( __FILE__, 'trynacbt_on_activation' );


function trynacbt_list_shortcode($atts = [], $content = null) {
  global $wpdb;
  $threads = $wpdb->get_results(
    "SELECT title, datetimePosted, uri
      FROM {$wpdb->prefix}trynacbt_threads
      WHERE datetimePosted > DATE_ADD(NOW(), INTERVAL -7 DAY)
      ORDER BY datetimePosted DESC"
  );

  $output = '<table>';
  $output .= '<thead><tr>';
  $output .= '<th>Thread</th>';
  $output .= '<th>Datetime Posted</th>';
  $output .= '</tr></thead><tbody>';

  foreach ($threads as $t) {
    $output .= '<tr>';
    $output .= '<td><a href="' . esc_attr(esc_url($t->uri)) . '">';
    $output .= esc_html($t->title);
    $output .= '</a></td>';
    $output .= '<td>' . esc_html($t->datetimePosted) . '</td>';
    $output .= '</tr>';
  }

  $output .= '</tbody></table>';

  return $output;
}
add_shortcode('trynacbt_list', 'trynacbt_list_shortcode');


/* Settings Page */
function trynacbt_settings_init() {
  register_setting('trynacbt', 'trynacbt_api_key');

  add_settings_section(
    'trynacbt_section'
    , 'trynacbt Settings'
    , 'trynacbt_on_settings_section'
    , 'trynacbt'
  );

  add_settings_field(
    'trynacbt_api_key'
    , 'API Key to accept from clients.'
    , 'trynacbt_on_field_api_key'
    , 'trynacbt'
    , 'trynacbt_section'
    , array(
      'label_for' => 'trynacbt_api_key'
    )
  );
}
add_action('admin_init', 'trynacbt_settings_init');

function trynacbt_on_settings_section($args) {
  ?>
    <p>Set the secret API key.</p>
  <?php
}

function trynacbt_on_field_api_key($args) {
  $apiKey = get_option('trynacbt_api_key');
  ?>
    <input id="<?php echo esc_attr( $args['label_for'] ); ?>"
        name="<?php echo esc_attr( $args['label_for'] ); ?>"
        value="<?php echo $apiKey ?: '' ?>"
    />
  <?php
}

function trynacbt_on_admin_menu() {
  add_menu_page(
    'trynacbt'
    , 'trynacbt'
    , 'manage_options'
    , 'trynacbt'
    , 'trynacbt_on_options_page'
  );
}
add_action('admin_menu', 'trynacbt_on_admin_menu');

function trynacbt_on_options_page() {
  if (!current_user_can('manage_options')) {
    return;
  }

  if (isset($_GET['settings-updated'])) {
    add_settings_error(
      'trynacbt_messages'
      , 'trynacbt_message'
      , 'Settings Saved'
      , 'success'
    );
  }

  settings_errors('trynacbt_messages');
  ?>
    <div class="wrap">
      <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
      <form action="options.php" method="post">
        <?php
          settings_fields('trynacbt');
          do_settings_sections('trynacbt');
          submit_button('Save Settings');
        ?>
      </form>
    </div>
  <?php
}


/* API */
function trynacbt_save_thread($title, $datetimePosted, $uri) {
  global $wpdb;
  $wpdb->query(
    $wpdb->prepare(
      "INSERT INTO {$wpdb->prefix}trynacbt_threads
        (title, datetimePosted, uri)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
          title = VALUES(title)
          , datetimePosted = VALUES(datetimePosted)
          , uri = VALUES(uri)
      "
      , $title
      , $datetimePosted
      , $uri
    )
  );
}
function trynacbt_on_api_sync($data) {
  if (!isset($data['apikey']) ||
      $data['apikey'] != get_option('trynacbt_api_key')) {
    return 'Incorrect apikey.';
  }

  $json = $data->get_json_params();
  $rowsSaved = 0;

  foreach ($json as $row) {
    trynacbt_save_thread($row['title'], $row['datetimePosted'], $row['uri']);
    $rowsSaved++;
  }

  return "{$rowsSaved} rows saved successfully.";
}
add_action( 'rest_api_init', function () {
  register_rest_route( 'trynacbt/v1', '/sync/', array(
    'methods' => 'POST',
    'callback' => 'trynacbt_on_api_sync',
  ));
});
?>
