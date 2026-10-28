Feature: ICS Cards home page
  As a visitor I want the home page to work so that I can find information about credit cards

  @smoke
  Scenario: Page title and metadata are correct
    Given I open the home page
    Then the page title matches "ICS .*creditcarduitgever"
    And the canonical link is "https://www.icscards.nl/"
    And the meta description contains "creditcard"
    And the html language is "nl"

  @smoke
  Scenario: Home page shows a main heading
    Given I open the home page
    Then the main heading is visible

  @smoke
  Scenario: Header shows private and business links
    Given I open the home page
    Then the "Privé" header link is the current page
    And the "Zakelijk" header link points to "/zakelijk"

  Scenario: Navigate to business
    Given I open the home page
    When I click the "Zakelijk" header link
    Then the url matches "/zakelijk/?$"

  Scenario: Menu button opens the menu dialog on mobile
    Given I open the home page
    And the viewport is 390 by 844
    When I click the open menu button
    Then a dialog is visible

  @responsive
  Scenario Outline: Home page renders at different viewports
    Given I open the home page
    And the viewport is <width> by <height>
    Then the main heading is visible

    Examples:
      | width | height |
      | 390   | 844    |
      | 1440  | 900    |

  Scenario: No broken internal links
    Given I open the home page
    Then the first 25 internal links respond without errors
