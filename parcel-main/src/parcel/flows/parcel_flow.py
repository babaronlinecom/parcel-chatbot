# Import Litellm's completion function (ensure litellm is installed)
from crewai.flow.flow import Flow, listen, start
from litellm import completion
from pydantic import BaseModel


# Define the state to store shipment and flow data.
class ParcelState(BaseModel):
    inquiry: str = ""
    parcel_type: str = ""
    weight: float = 0.0
    dimensions: dict = {}
    sender_address: str = ""
    receiver_address: str = ""
    special_instructions: str = ""
    shipping_cost: float = 0.0
    delivery_time: int = 0
    tracking_code: str = ""
    shipment_status: str = "pending"
    feedback: str = ""
    collaboration_report: dict = {}


# Define the Flow for the shipping process.
class ParcelShippingFlow(Flow[ParcelState]):
    # Set the model to use Litellm with Gemini-2.0-flash-exp.
    model = "gemini-2.0-flash-exp"

    @start()
    def validate_inquiry(self):
        # Simulate a customer inquiry with PDF extraction (can be replaced by a LangChain PDF tool).
        self.state.inquiry = (
            "I need to send a parcel to Pakistan. See attached document for details."
        )
        # Optionally, use litellm.completion to process the inquiry text.
        # response = completion(model=self.model, messages=[{"role": "user", "content": self.state.inquiry}])
        return "Inquiry validated and shipment details extracted."

    @listen(validate_inquiry)
    def calculate_rate(self, validation_output):
        # Simulated call to a rate calculator API.
        base_cost = 10.0
        weight_cost = 2.5 * 2.0  # using example weight
        dimensions = {"length": 30, "width": 20, "height": 10}
        dimension_cost = (
            dimensions["length"] * dimensions["width"] * dimensions["height"]
        ) / 1000.0
        self.state.shipping_cost = base_cost + weight_cost + dimension_cost
        self.state.delivery_time = 7  # days estimate
        # Optionally, call a LangChain tool here for dynamic rate lookup.
        return {
            "shipping_cost": self.state.shipping_cost,
            "delivery_time": self.state.delivery_time,
            "message": "Rate calculated. Proceed with shipment dispatch?",
        }

    @listen(calculate_rate)
    def dispatch_shipment(self, rate_details):
        # Simulated dispatch using a shipping API (e.g., Aramex Shipping Services).
        self.state.tracking_code = "AMXTRACK12345"
        return f"Shipment dispatched with tracking code {self.state.tracking_code}."

    @listen(dispatch_shipment)
    def track_shipment(self, dispatch_msg):
        # Simulated tracking using a tracking API and location services.
        status = "In Transit"
        location = "On route near Multan, Pakistan"
        self.state.shipment_status = status
        return {"status": status, "current_location": location}

    @listen(track_shipment)
    def collaborate_and_train(self, tracking_info):
        # Simulate collaboration and training (training routines could be added here).
        self.state.feedback = "Delivery is smooth and on schedule."
        self.state.collaboration_report = {
            "rate_details": {
                "cost": self.state.shipping_cost,
                "delivery_time": self.state.delivery_time,
            },
            "tracking_info": tracking_info,
            "feedback": self.state.feedback,
        }
        return self.state.collaboration_report

    @listen(collaborate_and_train)
    def analytics_reporting(self, collab_report):
        # Final reporting step.
        return {
            "final_shipping_cost": self.state.shipping_cost,
            "estimated_delivery_time": self.state.delivery_time,
            "tracking_code": self.state.tracking_code,
            "shipment_status": self.state.shipment_status,
            "collaboration_report": collab_report,
        }


def main():
    flow = ParcelShippingFlow()
    final_output = flow.kickoff()
    print("Final Output:", final_output)
    return final_output


if __name__ == "__main__":
    main()
