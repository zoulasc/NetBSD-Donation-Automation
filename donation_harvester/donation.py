import stripeapi
import paypalapi

stripe_api = stripeapi.StripeAPI(
    "sk_test_51NAtgCLWOZAy5SpfukpFqmUparmC3k1fZ0XURnV6o09EdmujE76eQjWtUGdhmOcrIPmVXApu3QACBps8LSy1jtXL00GBTG6CoE"
)
paypal_api = paypalapi.PaypalAPI("AUMGSf82bpVokGsmR59CRu3bNEppTQeCpX92tM-TYdBrRjjjFikidUtelVuhJDYAl_bySk_FpniFWmY_","EMomA8GmT2MD0UiVAyS-2PsyH8kZYGxncVbqLaCtbVaL-8jO_K7OMjb4bJ94YJT8VFWLyCcMrWZWsvjM")

def get_new_donations():
    donations = stripe_api.get_new_donations()

    return donations


def get_last_n(n):
    donations = stripe_api.get_all_charges(n)

    return donations
