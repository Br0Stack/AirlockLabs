<?php

    if ($_SERVER["REQUEST_METHOD"] == "POST") {

        # FIX: Replace this email with recipient email
        $mail_to = "{put yor email address here}";
        
        # Sender Data
        $subject = trim($_POST["subject"]);
        $name = str_replace(array("\r","\n"),array(" "," ") , strip_tags(trim($_POST["name"])));
        $email = filter_var(trim($_POST["email"]), FILTER_SANITIZE_EMAIL);
        $phone = trim($_POST["subject"]);
        $message = trim($_POST["message"]);
        $data_ownership = isset($_POST["data_ownership"]) ? trim($_POST["data_ownership"]) : "";
        
        if ( empty($name) OR !filter_var($email, FILTER_VALIDATE_EMAIL) OR empty($subject) OR empty($message) OR empty($data_ownership)) {
            # Set a 400 (bad request) response code and exit.
            http_response_code(400);
            echo "Please complete the form and confirm data ownership to proceed.";
            exit;
        }
        
        # Mail Content
        $content = "Name: $name\n";
        $content .= "Email: $email\n\n";
        $content .= "Subject: $subject\n";
        $content .= "Message:\n$message\n";
        $content .= "\nData ownership confirmed: yes\n";
        $content .= "Non-legal notice: This submission is informational and not legal advice.\n";
        $content .= "Cloud uploads are disabled by default; the message is prepared locally in the sender's browser and only sent on submission.\n";
        $content .= "Storage: Messages are kept only in the email inbox. Delete instantly by emailing with subject \"DELETE MY DATA\".\n";

        # email headers.
        $headers = "From: $name <$email>";

        # Send the email.
        $success = mail($mail_to, $subject, $content, $headers);
        if ($success) {
            # Set a 200 (okay) response code.
            http_response_code(200);
            echo "Thank You! Your message has been sent.";
        } else {
            # Set a 500 (internal server error) response code.
            http_response_code(500);
            echo "Oops! Something went wrong, we couldn't send your message.";
        }

    } else {
        # Not a POST request, set a 403 (forbidden) response code.
        http_response_code(403);
        echo "There was a problem with your submission, please try again.";
    }

?>
