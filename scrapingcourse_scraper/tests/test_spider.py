import unittest
import json
import re
from scrapy.http import HtmlResponse, Request
from scrapingcourse_scraper.spiders.scraper import ScraperSpider

class TestScraperSpider(unittest.TestCase):
    def setUp(self):
        self.spider = ScraperSpider()
        
    def _create_mock_response(self, html_content, url="https://uk.trip.com/hotels/", meta=None):
        # Create a mock request with a meta attribute
        request = Request(url=url, body=html_content.encode('utf-8'), encoding='utf-8', meta=meta or {})
        # Return a mock response tied to the request
        return HtmlResponse(url=url, request=request, body=html_content.encode('utf-8'), encoding='utf-8')
    
    def test_parse_method_with_valid_data(self):
        # Create a mock response with sample IBU_HOTEL data
        mock_html = """
        <html>
            <script>
            window.IBU_HOTEL = {
                "initData": {
                    "htlsData": {
                        "inboundCities": [
                            {"id": "123", "name": "Test City 1"},
                            {"id": "456", "name": "Test City 2"},
                            {"id": "789", "name": "Test City 3"}
                        ],
                        "outboundCities": [
                            {"id": "132", "name": "Test City 4"},
                            {"id": "453", "name": "Test City 5"},
                            {"id": "787", "name": "Test City 6"}
                        ]
                    }
                }
            };
            </script>
        </html>
        """
        
        # Create a mock response
        response = self._create_mock_response(mock_html)
        
        # Capture the requests generated by the parse method
        requests = list(self.spider.parse(response))
        
        # Assert that requests were generated
        self.assertTrue(len(requests) > 0)
        
        # Check that each request has the correct URL and meta
        for request in requests:
            self.assertTrue(hasattr(request, 'url'))
            self.assertTrue('city_id' in request.meta)
    
    def test_parse_method_with_no_cities(self):
        # Create a mock response with no cities
        mock_html = """
        <html>
            <script>
            window.IBU_HOTEL = {
                "initData": {
                    "htlsData": {}
                }
            };
            </script>
        </html>
        """
        
        # Create a mock response
        response = self._create_mock_response(mock_html)
        
        # Capture the requests generated by the parse method
        requests = list(self.spider.parse(response))
        
        # Assert that no requests were generated
        self.assertEqual(len(requests), 0)
    
    def test_parse_city_data_method(self):
        # Create a mock response with hotel data
        mock_html = """
        <html>
            <script>
            window.IBU_HOTEL = {
                "initData": {
                    "firstPageList": {
                        "hotelList": [
                            {
                                "hotelBasicInfo": {
                                    "hotelId": "123",
                                    "hotelName": "Test Hotel",
                                    "hotelAddress": "Test Address",
                                    "hotelImg": "https://www.w3schools.com/html/img_girl.jpg",
                                    "price": "100.50"
                                },
                                "commentInfo": {
                                    "commentScore": "4.5"
                                },
                                "roomInfo": {
                                    "physicalRoomName": "Standard Room"
                                },
                                "positionInfo": {
                                    "coordinate": {
                                        "lat": "40.7128",
                                        "lng": "-74.0060"
                                    }
                                }
                            }
                        ]
                    }
                }
            };
            </script>
        </html>
        """
        
        # Create a mock response with city_id in meta
        meta = {'city_id': '123'}
        response = self._create_mock_response(mock_html, meta=meta)
        
        # Capture the items generated by parse_city_data method
        items = list(self.spider.parse_city_data(response))
        
        # Assert that items were generated
        self.assertEqual(len(items), 1)
        
        # Check the structure of the generated item
        item = items[0]
        self.assertEqual(item['city_id'], '123')
        self.assertEqual(item['hotelName'], 'Test Hotel')
        self.assertEqual(item['hotelAddress'], 'Test Address')

if __name__ == '__main__':
    unittest.main()
