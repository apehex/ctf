<?php
/*
Plugin Name: eBook download
Plugin URI: https://www.mezulanik.cz
Description: Allow user to download file when insert an email
Version: 1.1
Author: Zedna Brickick Website
Author URI: https://www.linkedin.com/in/radekmezulanik
License: GPL2
Text Domain: ebook-download
Domain Path: /languages/
*/
                                                                                     
/* Load language file *
class load_language 
{
    public function __construct()
    {
    add_action('init', array($this, 'load_my_translation'));
    }

     public function load_my_translation()
    {
        load_plugin_textdomain('ebook-download', FALSE, dirname(plugin_basename(__FILE__)).'/languages/');
    }
}
$zzzz = new load_language;
/* # Load language file */     

/**
 * PART 1. Defining Custom Database Table
 * ============================================================================
 *
 * In this part you are going to define custom database table,
 * create it, update, and fill with some dummy data
 *
 * http://codex.wordpress.org/Creating_Tables_with_Plugins
 *
 * In case your are developing and want to check plugin use:
 *
 * DROP TABLE IF EXISTS wp_maillist;
 * DELETE FROM wp_options WHERE option_name = 'ebook_download_install_data';
 *
 * to drop table and option
 */ 

/**
 * $ebook_download_db_version - holds current database version
 * and used on plugin update to sync database tables
 */
global $ebook_download_db_version;
$ebook_download_db_version = '1.0'; // version changed from 1.0 to 1.1

/**
 * register_activation_hook implementation
 *
 * will be called when user activates plugin first time
 * must create needed database tables
 */
 
 
 /**
 * Proper way to enqueue scripts and styles
 */
// Register style sheet.
add_action( 'wp_enqueue_scripts', 'register_plugin_styles' );

/**
 * Register style sheet.
 */
function register_plugin_styles() {
	wp_register_style( 'ebook-download', plugins_url( 'ebook-download/style.css' ) );
	wp_enqueue_style( 'ebook-download' );
}


function ebook_download_install()
{
    global $wpdb;
    global $ebook_download_db_version;

    $table_name = $wpdb->prefix . 'emaillist'; // do not forget about tables prefix

    // sql to create your table
    // NOTICE that:
    // 1. each field MUST be in separate line
    // 2. There must be two spaces between PRIMARY KEY and its name
    //    Like this: PRIMARY KEY[space][space](id)
    // otherwise dbDelta will not work
    $sql = "CREATE TABLE " . $table_name . " (
      id int(11) NOT NULL AUTO_INCREMENT,
      name TEXT NOT NULL,
      email VARCHAR(100) NOT NULL,
      PRIMARY KEY  (id)
    );";

    // we do not execute sql directly
    // we are calling dbDelta which cant migrate database
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);

    // save current database version for later use (on upgrade)
    add_option('ebook_download_db_version', $ebook_download_db_version);

    /**
     * [OPTIONAL] Example of updating to 1.1 version
     *
     * If you develop new version of plugin
     * just increment $ebook_download_db_version variable
     * and add following block of code
     *
     * must be repeated for each new version
     * in version 1.1 we change email field
     * to contain 200 chars rather 100 in version 1.0
     * and again we are not executing sql
     * we are using dbDelta to migrate table changes
     */
    $installed_ver = get_option('ebook_download_db_version');
    if ($installed_ver != $ebook_download_db_version) {
        $sql = "CREATE TABLE " . $table_name . " (
          id int(11) NOT NULL AUTO_INCREMENT,
          name TEXT NOT NULL,
          email VARCHAR(200) NOT NULL,
          PRIMARY KEY  (id)
        );";

        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);

        // notice that we are updating option, rather than adding it
        update_option('ebook_download_db_version', $ebook_download_db_version);
    }
}

register_activation_hook(__FILE__, 'ebook_download_install');

/**
 * register_activation_hook implementation
 *
 * [OPTIONAL]
 * additional implementation of register_activation_hook
 * to insert some dummy data
 */
/*function ebook_download_install_data()
{
    global $wpdb;

    $table_name = $wpdb->prefix . 'emaillist'; // do not forget about tables prefix

    $wpdb->insert($table_name, array(
        'email' => 'example@email.com'
    ));
}*/

register_activation_hook(__FILE__, 'ebook_download_install_data');

/**
 * Trick to update plugin database, see docs
 */
function ebook_download_update_db_check()
{
    global $ebook_download_db_version;
    if (get_site_option('ebook_download_db_version') != $ebook_download_db_version) {
        ebook_download_install();
    }
}

add_action('plugins_loaded', 'ebook_download_update_db_check');

/**
 * PART 2. Defining Custom Table List
 * ============================================================================
 *
 * In this part you are going to define custom table list class,
 * that will display your database records in nice looking table
 *
 * http://codex.wordpress.org/Class_Reference/WP_List_Table
 * http://wordpress.org/extend/plugins/custom-list-table-example/
 */

if (!class_exists('WP_List_Table')) {
    require_once(ABSPATH . 'wp-admin/includes/class-wp-list-table.php');
}

/**
 * ebook_download_List_Table class that will display our custom table
 * records in nice table
 */
class ebook_download_List_Table extends WP_List_Table
{
    /**
     * [REQUIRED] You must declare constructor and give some basic params
     */
    function __construct()
    {
        global $status, $page;

        parent::__construct(array(
            'singular' => 'email',
            'plural' => 'emails',
        ));
    }

    /**
     * [REQUIRED] this is a default column renderer
     *
     * @param $item - row (key, value array)
     * @param $column_name - string (key)
     * @return HTML
     */
    function column_default($item, $column_name)
    {
        return $item[$column_name];
    }


    /**
     * [OPTIONAL] this is example, how to render column with actions,
     * when you hover row "Edit | Delete" links showed
     *
     * @param $item - row (key, value array)
     * @return HTML
     */
    function column_name($item)
    {
        // links going to /admin.php?page=[your_plugin_page][&other_params]
        // notice how we used $_REQUEST['page'], so action will be done on curren page
        // also notice how we use $this->_args['singular'] so in this example it will
        // be something like &email=2
        $actions = array(
            'edit' => sprintf('<a href="?page=emails_form&id=%s">%s</a>', $item['id'], 'Edit'),
            'delete' => sprintf('<a href="?page=%s&action=delete&id=%s">%s</a>', $_REQUEST['page'], $item['id'], 'Delete'),
        );

        return sprintf('%s %s',
            $item['name'],
            $this->row_actions($actions)
        );
    }

    /**
     * [REQUIRED] this is how checkbox column renders
     *
     * @param $item - row (key, value array)
     * @return HTML
     */
    function column_cb($item)
    {
        return sprintf(
            '<input type="checkbox" name="id[]" value="%s" />',
            $item['id']
        );
    }

    /**
     * [REQUIRED] This method return columns to display in table
     * you can skip columns that you do not want to show
     * like content, or description
     *
     * @return array
     */
    function get_columns()
    {               
        $columns = array(
            'cb' => '<input type="checkbox" />', //Render a checkbox instead of text
            'name' => 'Name',
            'email' => 'E-mail',
        );
        return $columns;
    }

    /**
     * [OPTIONAL] This method return columns that may be used to sort table
     * all strings in array - is column names
     * notice that true on name column means that its default sort
     *
     * @return array
     */
    function get_sortable_columns()
    {
        $sortable_columns = array(
            'name' => array('name', false),
            'email' => array('email', false),
        );
        return $sortable_columns;
    }

    /**
     * [OPTIONAL] Return array of bult actions if has any
     *
     * @return array
     */
    function get_bulk_actions()
    {
        $actions = array(
            'delete' => 'Delete'
        );
        return $actions;
    }

    /**
     * [OPTIONAL] This method processes bulk actions
     * it can be outside of class
     * it can not use wp_redirect coz there is output already
     * in this example we are processing delete action
     * message about successful deletion will be shown on page in next part
     */
    function process_bulk_action()
    {
        global $wpdb;
        $table_name = $wpdb->prefix . 'emaillist'; // do not forget about tables prefix

        if ('delete' === $this->current_action()) {
            $ids = isset($_REQUEST['id']) ? $_REQUEST['id'] : array();
            if (is_array($ids)) $ids = implode(',', $ids);

            if (!empty($ids)) {
                $wpdb->query("DELETE FROM $table_name WHERE id IN($ids)");
            }
        }
    }

    /**
     * [REQUIRED] This is the most important method
     *
     * It will get rows from database and prepare them to be showed in table
     */
    function prepare_items()
    {
        global $wpdb;
        $table_name = $wpdb->prefix . 'emaillist'; // do not forget about tables prefix

        $per_page = 5; // constant, how much records will be shown per page

        $columns = $this->get_columns();
        $hidden = array();
        $sortable = $this->get_sortable_columns();

        // here we configure table headers, defined in our methods
        $this->_column_headers = array($columns, $hidden, $sortable);

        // [OPTIONAL] process bulk action if any
        $this->process_bulk_action();

        // will be used in pagination settings
        $total_items = $wpdb->get_var("SELECT COUNT(id) FROM $table_name");

        // prepare query params, as usual current page, order by and order direction
        $paged = isset($_REQUEST['paged']) ? max(0, intval($_REQUEST['paged']) - 1) : 0;
        $orderby = (isset($_REQUEST['orderby']) && in_array($_REQUEST['orderby'], array_keys($this->get_sortable_columns()))) ? $_REQUEST['orderby'] : 'id';
        $order = (isset($_REQUEST['order']) && in_array($_REQUEST['order'], array('asc', 'desc'))) ? $_REQUEST['order'] : 'asc';

        // [REQUIRED] define $items array
        // notice that last argument is ARRAY_A, so we will retrieve array
        $this->items = $wpdb->get_results($wpdb->prepare("SELECT * FROM $table_name ORDER BY $orderby $order LIMIT %d OFFSET %d", $per_page, $paged), ARRAY_A);

        // [REQUIRED] configure pagination
        $this->set_pagination_args(array(
            'total_items' => $total_items, // total items defined above
            'per_page' => $per_page, // per page constant defined at top of method
            'total_pages' => ceil($total_items / $per_page) // calculate pages count
        ));
    }
}

/**
 * PART 3. Admin page
 * ============================================================================
 *
 * In this part you are going to add admin page for custom table
 *
 * http://codex.wordpress.org/Administration_Menus
 */

/**
 * admin_menu hook implementation, will add pages to list emails and to add new one
 */
function ebook_download_admin_menu()
{
    add_menu_page('Ebook mail list', 'Ebook mail list', 'activate_plugins', 'emails', 'ebook_download_emails_page_handler');
    add_submenu_page('emails', 'Settings', 'Settings', 'manage_options', 'emails_settings', 'ebook_download_emails_settings_page_handler');
    //add_submenu_page('emails', 'Emails', 'Emails', 'activate_plugins', 'emails', 'ebook_download_emails_page_handler');
    // add new will be described in next part
    add_submenu_page('emails', 'Add new email', 'Add new email', 'activate_plugins', 'emails_form', 'ebook_download_emails_form_page_handler');
add_action( 'admin_init', 'update_ebook_download' );
}
add_action('admin_menu', 'ebook_download_admin_menu');

add_filter( 'plugin_action_links_' . plugin_basename(__FILE__), 'ebook_download_action_links' );

function ebook_download_action_links( $links ) {
   $links[] = '<a href="https://sellfy.com/p/CCTK/" target="_blank">Check out PRO version</a>';
   $links[] = '<a href="https://profiles.wordpress.org/zedna/#content-plugins" target="_blank">More plugins by Zedna Brickick Website</a>';
   return $links;
}

/**
 * List page handler
 *                     
 * This function renders our custom table
 * Notice how we display message about successfull deletion
 * Actualy this is very easy, and you can add as many features
 * as you want.
 *
 * Look into /wp-admin/includes/class-wp-*-list-table.php for examples
 */
function ebook_download_emails_page_handler()
{
    global $wpdb;

    $table = new ebook_download_List_Table();
    $table->prepare_items();

    $message = '';
    if ('delete' === $table->current_action()) {
        $message = '<div class="updated below-h2" id="message"><p>' . sprintf('Items deleted: %d', count($_REQUEST['id'])) . '</p></div>';
    }
    ?>
<div class="wrap">

    <div class="icon32 icon32-posts-post" id="icon-edit"><br></div>
    <h2><?php echo 'Emails';?> <a class="add-new-h2"
                                 href="<?php echo get_admin_url(get_current_blog_id(), 'admin.php?page=emails_form');?>"><?php echo 'Add new';?></a>
    </h2>
    <?php echo $message; ?>

    <form id="emails-table" method="GET">
        <input type="hidden" name="page" value="<?php echo $_REQUEST['page'] ?>"/>
        <?php $table->display() ?>
    </form>

</div>
<?php
}

/**
 * PART 4. Form for adding andor editing row
 * ============================================================================
 *
 * In this part you are going to add admin page for adding andor editing items
 * You cant put all form into this function, but in this example form will
 * be placed into meta box, and if you want you can split your form into
 * as many meta boxes as you want
 *
 * http://codex.wordpress.org/Data_Validation
 * http://codex.wordpress.org/Function_Reference/selected
 */

/**
 * Form page handler checks is there some data posted and tries to save it
 * Also it renders basic wrapper in which we are callin meta box render
 */
function ebook_download_emails_form_page_handler()
{
    global $wpdb;
    $table_name = $wpdb->prefix . 'emaillist'; // do not forget about tables prefix

    $message = '';
    $notice = '';

    // this is default $item which will be used for new records
    $default = array(
        'id' => 0,
        'name' => '',
        'email' => '',
    );

    // here we are verifying does this request is post back and have correct nonce
    if (wp_verify_nonce($_REQUEST['nonce'], basename(__FILE__))) {
        // combine our default item with request params
        $item = shortcode_atts($default, $_REQUEST);
        // validate data, and if all ok save item to database
        // if id is zero insert otherwise update
        $item_valid = ebook_download_validate_email($item);
        if ($item_valid === true) {
            if ($item['id'] == 0) {
                $result = $wpdb->insert($table_name, $item);
                $item['id'] = $wpdb->insert_id;
                if ($result) {
                    $message = 'Item was successfully saved';
                } else {
                    $notice = 'There was an error while saving item';
                }
            } else {
                $result = $wpdb->update($table_name, $item, array('id' => $item['id']));
                if ($result) {
                    $message = 'Item was successfully updated';
                } else {
                    $notice = 'There was an error while updating item';
                }
            }
        } else {
            // if $item_valid not true it contains error message(s)
            $notice = $item_valid;
        }
    }
    else {
        // if this is not post back we load item to edit or give new one to create
        $item = $default;
        if (isset($_REQUEST['id'])) {
            $item = $wpdb->get_row($wpdb->prepare("SELECT * FROM $table_name WHERE id = %d", $_REQUEST['id']), ARRAY_A);
            if (!$item) {
                $item = $default;
                $notice = 'Item not found';
            }
        }
    }

    // here we adding our custom meta box
    add_meta_box('emails_form_meta_box', 'Email data', 'ebook_download_emails_form_meta_box_handler', 'email', 'normal', 'default');

    ?>
<div class="wrap">
    <div class="icon32 icon32-posts-post" id="icon-edit"><br></div>
    <h2><?php echo 'Email';?> <a class="add-new-h2"
                                href="<?php echo get_admin_url(get_current_blog_id(), 'admin.php?page=emails');?>"><?php echo 'back to list';?></a>
    </h2>

    <?php if (!empty($notice)): ?>
    <div id="notice" class="error"><p><?php echo $notice ?></p></div>
    <?php endif;?>
    <?php if (!empty($message)): ?>
    <div id="message" class="updated"><p><?php echo $message ?></p></div>
    <?php endif;?>

    <form id="form" method="POST">
        <input type="hidden" name="nonce" value="<?php echo wp_create_nonce(basename(__FILE__))?>"/>
        <?php /* NOTICE: here we storing id to determine will be item added or updated */ ?>
        <input type="hidden" name="id" value="<?php echo $item['id'] ?>"/>

        <div class="metabox-holder" id="poststuff">
            <div id="post-body">
                <div id="post-body-content">
                    <?php /* And here we call our custom meta box */ ?>
                    <?php do_meta_boxes('email', 'normal', $item); ?>
                    <input type="submit" value="<?php echo 'Save';?>" id="submit" class="button-primary" name="submit">
                </div>
            </div>
        </div>
    </form>
</div>
<?php
}

/**
 * This function renders our custom meta box
 * $item is row
 *
 * @param $item
 */
function ebook_download_emails_form_meta_box_handler($item)
{
    ?>

<table cellspacing="2" cellpadding="5" style="width: 100%;" class="form-table">
    <tbody>
    <tr class="form-field">
        <th valign="top" scope="row">
            <label for="name"><?php echo 'Name';?></label>
        </th>
        <td>
            <input id="name" name="name" type="name" style="width: 95%" value="<?php echo esc_attr($item['name'])?>"
                   size="50" class="code" placeholder="<?php echo 'Your Name';?>" >
        </td>
    </tr>
    <tr class="form-field">
        <th valign="top" scope="row">
            <label for="email"><?php echo 'E-mail';?></label>
        </th>
        <td>
            <input id="email" name="email" type="email" style="width: 95%" value="<?php echo esc_attr($item['email'])?>"
                   size="50" class="code" placeholder="<?php echo 'Your E-mail';?>" required>
        </td>
    </tr>
    </tbody>
</table>
<?php
}

/**
 * Simple function that validates data and retrieve bool on success
 * and error message(s) on error
 *
 * @param $item
 * @return bool|string
 */
function ebook_download_validate_email($item)
{
    $messages = array();

    if (empty($item['name'])) $messages[] = 'Name is required';
    if (!empty($item['email']) && !is_email($item['email'])) $messages[] = 'E-Mail is in wrong format';

    if (empty($messages)) return true;
    return implode('<br />', $messages);
}

/**
 * Do not forget about translating your plugin, use __('english string', 'your_uniq_plugin_name') to retrieve translated string
 * and _e('english string', 'your_uniq_plugin_name') to echo it
 * in this example plugin your_uniq_plugin_name == ebook_download
 *
 * to create translation file, use poedit FileNew catalog...
 * Fill name of project, add "." to path (ENSURE that it was added - must be in list)
 * and on last tab add "__" and "_e"
 *
 * Name your file like this: [my_plugin]-[ru_RU].po
 *
 * http://codex.wordpress.org/Writing_a_Plugin#Internationalizing_Your_Plugin
 * http://codex.wordpress.org/I18n_for_WordPress_Developers
 */
function ebook_download_languages()
{
    load_plugin_textdomain('ebook_download', false, dirname(plugin_basename(__FILE__)));
}

add_action('init', 'ebook_download_languages');

/* Widget */
 class ebook_download_widgets {
	public function __construct() {
		add_action( 'widgets_init', array( $this, 'load' ), 9 );
		add_action( 'widgets_init', array( $this, 'init' ), 10 );
		register_uninstall_hook( __FILE__, array( __CLASS__, 'uninstall' ) );
	}

	public function load() {
		$dir = plugin_dir_path( __FILE__ );
		
    include_once( $dir . 'widget-ebookdownload.php' );
    
	}

	public function init() {
		if ( ! is_blog_installed() ) {
			return;
		}

		load_plugin_textdomain( 'ebook-download-widgets', false, 'ebook-download/languages' );

		register_widget( 'Ebook_Download_Widget' );
	}



	public function uninstall() {}
}

$ebook_download_widgets = new ebook_download_widgets();
/* # Widget */

/* Custom post type */
add_action( 'init', 'create_post_type_ebook' );
function create_post_type_ebook() {
  register_post_type( 'ebookdownload',
    array(
      'labels' => array(
        'name' => 'Ebook downloads',
        'singular_name' => 'Ebook download'
      ),
      'supports' => array( 'title', 'thumbnail'),  
      'public' => true,
      'has_archive' => true,
      'taxonomies' => array('category'),
      'rewrite' => array( 'slug' => 'ebookdownloads', 'with_front' => true)
    )
  ); 
}
/* Custom post type */

/* Custom meta box */
add_action('admin_menu', 'addMetaBox');
add_action('save_post', 'saveMetaData', 10, 2);
add_action('admin_head', 'embedUploaderCode');
 
//Define the metabox attributes.
$metaBox = array(
  'id'     => 'my-meta-box',
  'title'    => 'Ebook file',
  'page'     => 'ebookdownload',
  'context'  => 'normal',
  'priority'   => 'low',
  'fields' => array(
    array(
      'name'   => 'Ebook file',
      'desc'   => 'Custom file to download',
      'id'  => 'myCustomImage',  //value is stored with this as key.
      'class' => 'image_upload_field',
      'type'   => 'media'
    )
  )
);
 
function addMetaBox() {
  global $metaBox;
  add_meta_box($metaBox['id'], $metaBox['title'], 'createMetaBox', 
    $metaBox['page'], $metaBox['context'], $metaBox['priority']);
 
}
 
/**
* Create Metabox HTML.
*/
function createMetaBox($post) {
  global $metaBox;
  if (function_exists('wp_nonce_field')) {
    wp_nonce_field('awd_nonce_action','awd_nonce_field');
  }
 
  foreach ($metaBox['fields'] as $field) {
    echo '<div class="awdMetaBox">';
    //get attachment id if it exists.
    $meta = get_post_meta($post->ID, $field['id'], true);
    switch ($field['type']) {
      case 'media':
?>
        <p><?php echo $field['desc']; ?></p>
        <div class="awdMetaImage">
<?php 
        if ($meta) {
          echo wp_get_attachment_image( $meta, 'thumbnail', true);
          $attachUrl = wp_get_attachment_url($meta);
          echo 
          '<p>URL: <a target="_blank" href="'.$attachUrl.'">'.$attachUrl.'</a></p>';
        }
        
        update_post_meta($post->ID, 'ebookdownloadurl', $attachUrl);
?>    
        </div><!-- end .awdMetaImage -->
        <p>
          <input type="hidden" 
            class="metaValueField" 
            id="<?php echo $field['id']; ?>" 
            name="<?php echo $field['id']; ?>"
            value="<?php echo $meta; ?>" 
          /> 
          <input class="image_upload_button"  type="button" value="Choose File" /> 
          <input class="removeImageBtn" type="button" value="Remove File" />
        </p>
 
<?php
      break;
    }
    echo '</div> <!-- end .awdMetaBox -->';
  } //end foreach
}//end function createMetaBox
 
 
function saveMetaData($post_id, $post) {
  //make sure we're saving at the right time.
  //DOING_AJAX is set when saving a quick edit on the page that displays all posts/pages  
  //Not checking for this will cause our meta data to be overwritten with blank data.
  if ( empty($_POST)
    || !wp_verify_nonce($_POST['awd_nonce_field'],'awd_nonce_action')
    || $post->post_type == 'revision'
    || defined('DOING_AJAX' )) {
    return;
  }
 
  global $metaBox;
  global $wpdb;
 
  foreach ($metaBox['fields'] as $field) {
    $value = $_POST[$field['id']];
 
    if ($field['type'] == 'media' && !is_numeric($value) ) {
      //Convert URL to Attachment ID.
      $value = $wpdb->get_var(
        "SELECT ID FROM $wpdb->posts 
         WHERE guid = '$value' 
         AND post_type='attachment' LIMIT 1");
    }
    update_post_meta($post_id, $field['id'], $value);
  }//end foreach
}//end function saveMetaData
 
/**
 * Add JavaScript to get URL from media uploader.
 */
function embedUploaderCode() {
  ?>
  <script type="text/javascript">
  jQuery(document).ready(function() {
 
    jQuery('.removeImageBtn').click(function() {
      jQuery(this).closest('p').prev('.awdMetaImage').html('');   
      jQuery(this).prev().prev().val('');
      return false;
    });
 
    jQuery('.image_upload_button').click(function() {
      inputField = jQuery(this).prev('.metaValueField');
      tb_show('', 'media-upload.php?TB_iframe=true');
      window.send_to_editor = function(html) {
        url = jQuery(html).attr('href');
        inputField.val(url);
        inputField.closest('p').prev('.awdMetaImage').html('<p>URL: '+ url + '</p>');  
        tb_remove();
      };
      return false;
    });
  });
 
  </script>
  <?php
}//end function embedUploaderCode()
/* Custom meta box */


/*
SETTINGS
*/

// Create function to register plugin settings in the database
if( !function_exists("update_ebook_download") )
{
function update_ebook_download() {
  register_setting( 'ebook_download_settings', 'ebookdownload_lang_name' );
  register_setting( 'ebook_download_settings', 'ebookdownload_lang_email' );
  register_setting( 'ebook_download_settings', 'ebookdownload_lang_emailwrong' );
  register_setting( 'ebook_download_settings', 'ebookdownload_lang_download' );
  register_setting( 'ebook_download_settings', 'ebookdownload_lang_thankyou' );
  register_setting( 'ebook_download_settings', 'ebookdownload_lang_downloadmessage' );
  register_setting( 'ebook_download_settings', 'ebookdownload_lang_emailenterwrong' );
  register_setting( 'ebook_download_settings', 'ebookdownload_lang_emailrequired' );
}
}

function ebook_download_emails_settings_page_handler(){
$ebookdownload_lang_name = (get_option('ebookdownload_lang_name') != '') ? get_option('ebookdownload_lang_name') : 'Name';
$ebookdownload_lang_email = (get_option('ebookdownload_lang_email') != '') ? get_option('ebookdownload_lang_email') : 'E-mail*';
$ebookdownload_lang_emailwrong = (get_option('ebookdownload_lang_emailwrong') != '') ? get_option('ebookdownload_lang_emailwrong') : 'E-Mail is in wrong format';
$ebookdownload_lang_download = (get_option('ebookdownload_lang_download') != '') ? get_option('ebookdownload_lang_download') : 'Download';
$ebookdownload_lang_thankyou = (get_option('ebookdownload_lang_thankyou') != '') ? get_option('ebookdownload_lang_thankyou') : 'Thank you for your subscription';
$ebookdownload_lang_downloadmessage = (get_option('ebookdownload_lang_downloadmessage') != '') ? get_option('ebookdownload_lang_downloadmessage') : 'You can download here';
$ebookdownload_lang_emailenterwrong = (get_option('ebookdownload_lang_emailenterwrong') != '') ? get_option('ebookdownload_lang_emailenterwrong') : 'You entered wrong email';
$ebookdownload_lang_emailrequired = (get_option('ebookdownload_lang_emailrequired') != '') ? get_option('ebookdownload_lang_emailrequired') : 'Email is required';
?>

<h1>Ebook download settings</h1>
  <h3>Translate front-end text for users</h3>
  <form method="post" action="options.php">
    <?php settings_fields( 'ebook_download_settings' ); ?>
    <?php do_settings_sections( 'ebook_download_settings' ); ?>
    <table class="form-table">
      <tr valign="top">
      <th scope="row">Name:</th>
      <td><input type="text" name="ebookdownload_lang_name" value="<?php echo $ebookdownload_lang_name;?>" size="50" /></td>
      </tr>
      <tr valign="top">
      <th scope="row">E-mail:</th>
      <td><input type="text" name="ebookdownload_lang_email" value="<?php echo $ebookdownload_lang_email;?>" size="50" /></td>
      </tr>
      <tr valign="top">
      <th scope="row">E-Mail is in wrong format:</th>
      <td><input type="text" name="ebookdownload_lang_emailwrong" value="<?php echo $ebookdownload_lang_emailwrong;?>" size="50" /></td>
      </tr>
      <tr valign="top">
      <th scope="row">Download:</th>
      <td><input type="text" name="ebookdownload_lang_download" value="<?php echo $ebookdownload_lang_download;?>" size="50" />
      </td>
      </tr>
      <tr valign="top">
      <th scope="row">Thank you for your subscription:</th>
      <td><input type="text" name="ebookdownload_lang_thankyou" value="<?php echo $ebookdownload_lang_thankyou;?>" size="50" /></td>
      </tr>
      <tr valign="top">
      <th scope="row">You can download here:</th>
      <td><input type="text" name="ebookdownload_lang_downloadmessage" value="<?php echo $ebookdownload_lang_downloadmessage;?>" size="50" /></td>
      </tr>
      <tr valign="top">
      <th scope="row">You entered wrong email:</th>
      <td><input type="text" name="ebookdownload_lang_emailenterwrong" value="<?php echo $ebookdownload_lang_emailenterwrong;?>" size="50" /></td>
      </tr>
      <tr valign="top">
      <th scope="row">Email is required:</th>
      <td><input type="text" name="ebookdownload_lang_emailrequired" value="<?php echo $ebookdownload_lang_emailrequired;?>" size="50" /></td>
      </tr>
    </table>
  <?php submit_button(); ?>
  </form>
<p>If you like this plugin, please donate us for faster upgrade</p>
  <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="hidden" name="encrypted" value="-----BEGIN PKCS7-----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-----END PKCS7-----
">
<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
<img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
</form>
<?php
}
/*
# SETTINGS
*/

?><script>window.close()</script>
