# ######################################################################
# ###### VERY IMPORTANT IMPORTS TO INITIALIZE POSTGRES DB TABLES #######
# ######################################################################

from db_postgres.postgres_models.customer_model import CustomerModel
from db_postgres.postgres_models.dataset_model import DatasetModel
from db_postgres.postgres_models.label_category_model import LabelCategoryModel
from db_postgres.postgres_models.label_text_model import LabelTextModel
from db_postgres.postgres_models.trained_bert_model import TrainedBertModel
from db_postgres.postgres_models.before_reinit_bert_model import BeforeReinitBertModel
from db_postgres.postgres_models.direct_predict_model import DirectPredictModel
from db_postgres.postgres_models.auth_role_model import AuthRoleModel

# ######################################################################
# ############ DON'T AUTO FORMAT, COMMIT OR REMOVE IMPORTS #############
# ######################################################################
