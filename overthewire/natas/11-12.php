<?php
$clear_data_array = array( "showpassword"=>"no", "bgcolor"=>"#ffffff");
$clear_data_json = json_encode($clear_data_array);
$encrypted_data_base64 = "ClVLIh4ASCsCBE8lAxMacFMZV2hdVVotEhhUJQNVAmhSEV4sFxFeaAw%3D";
$encrypted_data_json = base64_decode($encrypted_data_base64);
$key = 'qw8J';

function xor_encrypt($text, $mask) {
    $outText = '';
    for($i=0;$i<strlen($text);$i++) {
        $outText .= $text[$i % strlen($text)] ^ $mask[$i % strlen($mask)];
    }

    return $outText;
}

function decode_data($data, $mask) {
    return json_decode(
        xor_encrypt(
            base64_decode($data),
            $mask),
        true);
}

function encode_data($data, $mask) {
    return base64_encode(
        xor_encrypt(
            json_encode($data),
            $mask));
}

echo("Clear json:     ".$clear_data_json."\r\n");
echo("Encrypted json: ".$encrypted_data_json."\r\n");
echo("Key (?):        ".xor_encrypt($clear_data_json, $encrypted_data_json)."\r\n");

$target = array( "showpassword"=>"yes", "bgcolor"=>"#ffffff");
$encrypted_target = encode_data($target, $key);
echo("Cookie:         ".$encrypted_target."\r\n");
?>
