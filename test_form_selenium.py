import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path


class TestContactForm(unittest.TestCase):
    """Test suite for the contact form in web_application.html"""
    
    @classmethod
    def setUpClass(cls):
        """Initialize WebDriver before all tests"""
        # Set up Chrome WebDriver
        options = webdriver.ChromeOptions()
        # Uncomment the line below to run headless (no GUI window)
        # options.add_argument("--headless")
        cls.driver = webdriver.Chrome(options=options)
        
        # Get the path to the HTML file
        html_path = Path(__file__).parent / "web_application.html"
        cls.driver.get(f"file:///{html_path.absolute()}")
        
        # Wait for page to load and form to be available
        wait = WebDriverWait(cls.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "contactForm")))
        time.sleep(1)
    
    @classmethod
    def tearDownClass(cls):
        """Close WebDriver after all tests"""
        try:
            cls.driver.quit()
        except:
            pass
    
    def setUp(self):
        """Reset form before each test"""
        try:
            # Wait for form to be present
            wait = WebDriverWait(self.driver, 10)
            form = wait.until(EC.presence_of_element_located((By.ID, "contactForm")))
            
            # Scroll to form
            self.driver.execute_script("arguments[0].scrollIntoView();", form)
            time.sleep(0.3)
            
            # Reset form
            self.driver.execute_script("document.getElementById('contactForm').reset();")
            time.sleep(0.2)
            
            # Hide any previous messages
            self.driver.execute_script("""
                const messageDiv = document.getElementById('formMessage');
                if (messageDiv) {
                    messageDiv.style.display = 'none';
                    messageDiv.textContent = '';
                }
            """)
        except Exception as e:
            print(f"Setup error: {e}")
            raise
    
    def test_form_exists(self):
        """Test that the form exists on the page"""
        form = self.driver.find_element(By.ID, "contactForm")
        self.assertIsNotNone(form)
        print("✓ Form exists on the page")
    
    def test_all_form_fields_exist(self):
        """Test that all required form fields are present"""
        field_ids = ["fullName", "emailAddress", "projectType", "messageBox", 
                     "agreeCheckbox", "newsletterCheckbox", "submitBtn"]
        
        for field_id in field_ids:
            element = self.driver.find_element(By.ID, field_id)
            self.assertIsNotNone(element)
        
        print("✓ All form fields exist")
    
    def test_successful_form_submission(self):
        """Test successful form submission with valid data"""
        # Fill out form with valid data
        self.driver.find_element(By.ID, "fullName").send_keys("Sukhada Bhoyar")
        self.driver.find_element(By.ID, "emailAddress").send_keys("sukhadabhoyar@gmail.com")
        
        # Select dropdown option
        project_dropdown = Select(self.driver.find_element(By.ID, "projectType"))
        project_dropdown.select_by_value("website")
        
        self.driver.find_element(By.ID, "messageBox").send_keys("I need a new website for my business")
        
        # Check required checkbox
        agree_checkbox = self.driver.find_element(By.ID, "agreeCheckbox")
        if not agree_checkbox.is_selected():
            agree_checkbox.click()
        
        # Submit form
        self.driver.find_element(By.ID, "submitBtn").click()
        
        # Wait for success message
        wait = WebDriverWait(self.driver, 10)
        message_div = wait.until(lambda driver: (
            driver.find_element(By.ID, "formMessage").is_displayed() and
            "Thank you" in driver.find_element(By.ID, "formMessage").text
        ))
        
        # Verify success message
        success_text = self.driver.find_element(By.ID, "formMessage").text
        self.assertIn("Thank you", success_text)
        self.assertIn("get back to you soon", success_text)
        
        print("✓ Form submission successful with valid data")
    
    def test_form_reset_after_submission(self):
        """Test that form is reset after successful submission"""
        # Fill and submit form
        self.driver.find_element(By.ID, "fullName").send_keys("Sukhada Bhoyar")
        self.driver.find_element(By.ID, "emailAddress").send_keys("sukhadabhoyar@gmail.com")
        
        project_dropdown = Select(self.driver.find_element(By.ID, "projectType"))
        project_dropdown.select_by_value("webapp")
        
        self.driver.find_element(By.ID, "messageBox").send_keys("I need a web application")
        
        agree_checkbox = self.driver.find_element(By.ID, "agreeCheckbox")
        if not agree_checkbox.is_selected():
            agree_checkbox.click()
        
        self.driver.find_element(By.ID, "submitBtn").click()
        
        # Wait for success message to appear
        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda driver: (
            driver.find_element(By.ID, "formMessage").is_displayed() and
            "Thank you" in driver.find_element(By.ID, "formMessage").text
        ))
        
        time.sleep(0.5)
        
        # Verify form is reset
        full_name_value = self.driver.find_element(By.ID, "fullName").get_attribute("value")
        email_value = self.driver.find_element(By.ID, "emailAddress").get_attribute("value")
        message_value = self.driver.find_element(By.ID, "messageBox").get_attribute("value")
        
        self.assertEqual(full_name_value, "")
        self.assertEqual(email_value, "")
        self.assertEqual(message_value, "")
        
        print("✓ Form reset after successful submission")
    
    def test_missing_full_name(self):
        """Test validation error when full name is missing"""
        self.driver.find_element(By.ID, "emailAddress").send_keys("test@example.com")
        self.driver.find_element(By.ID, "messageBox").send_keys("Test message")
        
        project_dropdown = Select(self.driver.find_element(By.ID, "projectType"))
        project_dropdown.select_by_value("website")
        
        agree_checkbox = self.driver.find_element(By.ID, "agreeCheckbox")
        if not agree_checkbox.is_selected():
            agree_checkbox.click()
        
        self.driver.find_element(By.ID, "submitBtn").click()
        time.sleep(0.5)
        
        # Verify error message
        message_div = self.driver.find_element(By.ID, "formMessage")
        self.assertIn("full name", message_div.text.lower())
        
        print("✓ Validation error for missing full name")
    
    def test_invalid_email(self):
        """Test validation error for invalid email"""
        self.driver.find_element(By.ID, "fullName").send_keys("Sukhada Bhoyar")
        self.driver.find_element(By.ID, "emailAddress").send_keys("invalid-email")
        self.driver.find_element(By.ID, "messageBox").send_keys("Test message")
        
        project_dropdown = Select(self.driver.find_element(By.ID, "projectType"))
        project_dropdown.select_by_value("website")
        
        agree_checkbox = self.driver.find_element(By.ID, "agreeCheckbox")
        if not agree_checkbox.is_selected():
            agree_checkbox.click()
        
        self.driver.find_element(By.ID, "submitBtn").click()
        time.sleep(0.5)
        
        # Verify error message
        message_div = self.driver.find_element(By.ID, "formMessage")
        self.assertIn("email", message_div.text.lower())
        
        print("✓ Validation error for invalid email")
    
    def test_missing_project_type(self):
        """Test validation error when project type is not selected"""
        self.driver.find_element(By.ID, "fullName").send_keys("Sukhada Bhoyar")
        self.driver.find_element(By.ID, "emailAddress").send_keys("sukhadabhoyar@gmail.com")
        self.driver.find_element(By.ID, "messageBox").send_keys("Test message")
        
        agree_checkbox = self.driver.find_element(By.ID, "agreeCheckbox")
        if not agree_checkbox.is_selected():
            agree_checkbox.click()
        
        self.driver.find_element(By.ID, "submitBtn").click()
        time.sleep(0.5)
        
        # Verify error message
        message_div = self.driver.find_element(By.ID, "formMessage")
        self.assertIn("project type", message_div.text.lower())
        
        print("✓ Validation error for missing project type")
    
    def test_missing_message(self):
        """Test validation error when message is empty"""
        self.driver.find_element(By.ID, "fullName").send_keys("Sukhada Bhoyar")
        self.driver.find_element(By.ID, "emailAddress").send_keys("sukhadabhoyar@gmail.com")
        
        project_dropdown = Select(self.driver.find_element(By.ID, "projectType"))
        project_dropdown.select_by_value("website")
        
        agree_checkbox = self.driver.find_element(By.ID, "agreeCheckbox")
        if not agree_checkbox.is_selected():
            agree_checkbox.click()
        
        self.driver.find_element(By.ID, "submitBtn").click()
        time.sleep(0.5)
        
        # Verify error message
        message_div = self.driver.find_element(By.ID, "formMessage")
        self.assertIn("message", message_div.text.lower())
        
        print("✓ Validation error for missing message")
    
    def test_unchecked_agreement_checkbox(self):
        """Test validation error when agreement checkbox is not checked"""
        self.driver.find_element(By.ID, "fullName").send_keys("Sukhada Bhoyar")
        self.driver.find_element(By.ID, "emailAddress").send_keys("sukhadabhoyar@gmail.com")
        
        project_dropdown = Select(self.driver.find_element(By.ID, "projectType"))
        project_dropdown.select_by_value("website")
        
        self.driver.find_element(By.ID, "messageBox").send_keys("Test message")
        
        # Don't check the agreement checkbox
        self.driver.find_element(By.ID, "submitBtn").click()
        time.sleep(0.5)
        
        # Verify error message
        message_div = self.driver.find_element(By.ID, "formMessage")
        self.assertIn("agree", message_div.text.lower())
        
        print("✓ Validation error for unchecked agreement checkbox")
    
    def test_checkbox_interactions(self):
        """Test checkbox toggle functionality"""
        agree_checkbox = self.driver.find_element(By.ID, "agreeCheckbox")
        newsletter_checkbox = self.driver.find_element(By.ID, "newsletterCheckbox")
        
        # Test unchecked state
        self.assertFalse(agree_checkbox.is_selected())
        self.assertFalse(newsletter_checkbox.is_selected())
        
        # Check agree checkbox
        agree_checkbox.click()
        self.assertTrue(agree_checkbox.is_selected())
        
        # Check newsletter checkbox
        newsletter_checkbox.click()
        self.assertTrue(newsletter_checkbox.is_selected())
        
        # Uncheck newsletter checkbox
        newsletter_checkbox.click()
        self.assertFalse(newsletter_checkbox.is_selected())
        
        print("✓ Checkbox interactions work correctly")
    
    def test_dropdown_options(self):
        """Test dropdown selection options"""
        dropdown = Select(self.driver.find_element(By.ID, "projectType"))
        
        # Get all options
        options = dropdown.options
        option_values = [option.get_attribute("value") for option in options]
        
        # Verify expected options exist
        expected_options = ["", "website", "webapp", "consultation", "other"]
        for expected in expected_options:
            self.assertIn(expected, option_values)
        
        # Test selecting each option
        dropdown.select_by_value("consultation")
        self.assertEqual(dropdown.first_selected_option.get_attribute("value"), "consultation")
        
        dropdown.select_by_value("other")
        self.assertEqual(dropdown.first_selected_option.get_attribute("value"), "other")
        
        print("✓ Dropdown options work correctly")
    
    def test_form_fields_accept_input(self):
        """Test that form fields accept user input"""
        test_data = {
            "fullName": "Test User Name",
            "emailAddress": "test@testmail.com",
            "messageBox": "This is a test message with multiple lines.\nLine 2\nLine 3"
        }
        
        for field_id, value in test_data.items():
            field = self.driver.find_element(By.ID, field_id)
            field.clear()
            field.send_keys(value)
            actual_value = field.get_attribute("value")
            self.assertEqual(actual_value, value)
        
        print("✓ Form fields accept input correctly")
    
    def test_submit_button_exists_and_visible(self):
        """Test that submit button is visible and clickable"""
        submit_btn = self.driver.find_element(By.ID, "submitBtn")
        self.assertTrue(submit_btn.is_displayed())
        self.assertTrue(submit_btn.is_enabled())
        self.assertEqual(submit_btn.text, "Send Message")
        
        print("✓ Submit button is visible and clickable")
    
    def test_form_message_display(self):
        """Test that form message container exists"""
        message_div = self.driver.find_element(By.ID, "formMessage")
        self.assertIsNotNone(message_div)
        
        # Initially should be hidden
        display_value = self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).display;", 
            message_div
        )
        self.assertEqual(display_value, "none")
        
        print("✓ Form message container works correctly")
    
    def test_multiple_form_submissions(self):
        """Test multiple form submissions with different data"""
        test_cases = [
            {
                "name": "Sukhada Bhoyar",
                "email": "sukhadabhoyar@gmail.com",
                "project": "website",
                "message": "First submission"
            },
            {
                "name": "Sukhada Bhoyar",
                "email": "sukhadabhoyar@gmail.com",
                "project": "webapp",
                "message": "Second submission"
            }
        ]
        
        for test_case in test_cases:
            self.driver.find_element(By.ID, "fullName").send_keys(test_case["name"])
            self.driver.find_element(By.ID, "emailAddress").send_keys(test_case["email"])
            
            project_dropdown = Select(self.driver.find_element(By.ID, "projectType"))
            project_dropdown.select_by_value(test_case["project"])
            
            self.driver.find_element(By.ID, "messageBox").send_keys(test_case["message"])
            
            agree_checkbox = self.driver.find_element(By.ID, "agreeCheckbox")
            if not agree_checkbox.is_selected():
                agree_checkbox.click()
            
            self.driver.find_element(By.ID, "submitBtn").click()
            time.sleep(1)
            
            # Verify success
            message_div = self.driver.find_element(By.ID, "formMessage")
            self.assertIn("Thank you", message_div.text)
        
        print("✓ Multiple form submissions work correctly")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
