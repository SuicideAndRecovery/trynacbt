<?php
  if (!defined('WP_UNINSTALL_PLUGIN')) {
      die;
  }

  global $wpdb;

  /* Remove tables. */
  $wpdb->query("DROP TABLE IF EXISTS {$wpdb->prefix}trynacbt_threads");

  /* Remove shortcode. */
  if (shortcode_exists('trynacbt_list')) {
    remove_shortcode('trynacbt_list');
  }
?>
