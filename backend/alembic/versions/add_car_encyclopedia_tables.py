"""add car encyclopedia tables

Revision ID: a1b2c3d4e5f6
Revises: df5ee69f89fe
Create Date: 2025-11-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'df5ee69f89fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add car encyclopedia tables."""

    # Create car_brands table
    op.create_table('car_brands',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.Column('founded_year', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reputation_score', sa.Integer(), nullable=True),
        sa.Column('reliability_rating', sa.Integer(), nullable=True),
        sa.Column('quality_rating', sa.Integer(), nullable=True),
        sa.Column('innovation_rating', sa.Integer(), nullable=True),
        sa.Column('advantages', JSON, nullable=True),
        sa.Column('disadvantages', JSON, nullable=True),
        sa.Column('specialties', JSON, nullable=True),
        sa.Column('popular_models', JSON, nullable=True),
        sa.Column('price_range', sa.String(), nullable=True),
        sa.Column('market_segment', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_car_brands_name', 'car_brands', ['name'])

    # Create engines table
    op.create_table('engines',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=True),
        sa.Column('fuel_type', sa.String(), nullable=False),
        sa.Column('engine_type', sa.String(), nullable=True),
        sa.Column('aspiration', sa.String(), nullable=True),
        sa.Column('displacement', sa.Integer(), nullable=True),
        sa.Column('cylinders', sa.Integer(), nullable=True),
        sa.Column('configuration', sa.String(), nullable=True),
        sa.Column('valves', sa.Integer(), nullable=True),
        sa.Column('power_hp', sa.Integer(), nullable=True),
        sa.Column('power_kw', sa.Integer(), nullable=True),
        sa.Column('torque_nm', sa.Integer(), nullable=True),
        sa.Column('max_torque_rpm', sa.String(), nullable=True),
        sa.Column('top_speed', sa.Integer(), nullable=True),
        sa.Column('acceleration_0_100', sa.String(), nullable=True),
        sa.Column('consumption_urban', sa.String(), nullable=True),
        sa.Column('consumption_extra_urban', sa.String(), nullable=True),
        sa.Column('consumption_combined', sa.String(), nullable=True),
        sa.Column('co2_emissions', sa.Integer(), nullable=True),
        sa.Column('euro_norm', sa.String(), nullable=True),
        sa.Column('battery_capacity', sa.String(), nullable=True),
        sa.Column('electric_range', sa.Integer(), nullable=True),
        sa.Column('charging_time', sa.String(), nullable=True),
        sa.Column('technologies', JSON, nullable=True),
        sa.Column('reliability_rating', sa.Integer(), nullable=True),
        sa.Column('maintenance_cost', sa.String(), nullable=True),
        sa.Column('known_issues', JSON, nullable=True),
        sa.Column('pros', JSON, nullable=True),
        sa.Column('cons', JSON, nullable=True),
        sa.Column('ideal_for', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_engines_fuel_type', 'engines', ['fuel_type'])
    op.create_index('ix_engines_power_hp', 'engines', ['power_hp'])

    # Create transmissions table
    op.create_table('transmissions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('gears', sa.Integer(), nullable=True),
        sa.Column('technology', sa.String(), nullable=True),
        sa.Column('manufacturer', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('shift_speed', sa.String(), nullable=True),
        sa.Column('efficiency', sa.String(), nullable=True),
        sa.Column('reliability_rating', sa.Integer(), nullable=True),
        sa.Column('maintenance_cost', sa.String(), nullable=True),
        sa.Column('known_issues', JSON, nullable=True),
        sa.Column('pros', JSON, nullable=True),
        sa.Column('cons', JSON, nullable=True),
        sa.Column('ideal_for', sa.Text(), nullable=True),
        sa.Column('typical_applications', JSON, nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_transmissions_type', 'transmissions', ['type'])

    # Create car_models table
    op.create_table('car_models',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('brand_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('generation', sa.String(), nullable=True),
        sa.Column('year_start', sa.Integer(), nullable=True),
        sa.Column('year_end', sa.Integer(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('body_type', sa.String(), nullable=True),
        sa.Column('segment', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('images', JSON, nullable=True),
        sa.Column('length', sa.Integer(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('wheelbase', sa.Integer(), nullable=True),
        sa.Column('trunk_capacity', sa.Integer(), nullable=True),
        sa.Column('weight', sa.Integer(), nullable=True),
        sa.Column('max_weight', sa.Integer(), nullable=True),
        sa.Column('seats', sa.Integer(), nullable=True),
        sa.Column('doors', sa.Integer(), nullable=True),
        sa.Column('price_new_min', sa.Integer(), nullable=True),
        sa.Column('price_new_max', sa.Integer(), nullable=True),
        sa.Column('price_used_avg', sa.Integer(), nullable=True),
        sa.Column('avg_consumption', sa.String(), nullable=True),
        sa.Column('co2_emissions', sa.Integer(), nullable=True),
        sa.Column('top_speed', sa.Integer(), nullable=True),
        sa.Column('acceleration_0_100', sa.String(), nullable=True),
        sa.Column('standard_equipment', JSON, nullable=True),
        sa.Column('optional_equipment', JSON, nullable=True),
        sa.Column('safety_features', JSON, nullable=True),
        sa.Column('tech_features', JSON, nullable=True),
        sa.Column('safety_rating', sa.Integer(), nullable=True),
        sa.Column('reliability_score', sa.Integer(), nullable=True),
        sa.Column('owner_satisfaction', sa.Integer(), nullable=True),
        sa.Column('pros', JSON, nullable=True),
        sa.Column('cons', JSON, nullable=True),
        sa.Column('available_engines', JSON, nullable=True),
        sa.Column('available_transmissions', JSON, nullable=True),
        sa.Column('competitors', JSON, nullable=True),
        sa.Column('ideal_for', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['brand_id'], ['car_brands.id'], ondelete='CASCADE')
    )
    op.create_index('ix_car_models_brand_id', 'car_models', ['brand_id'])
    op.create_index('ix_car_models_name', 'car_models', ['name'])
    op.create_index('ix_car_models_year_start', 'car_models', ['year_start'])
    op.create_index('ix_car_models_year_end', 'car_models', ['year_end'])
    op.create_index('ix_car_models_price_new_min', 'car_models', ['price_new_min'])

    # Create technical_specifications table
    op.create_table('technical_specifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('model_id', sa.String(), nullable=False),
        sa.Column('version_name', sa.String(), nullable=False),
        sa.Column('trim_level', sa.String(), nullable=True),
        sa.Column('engine_id', sa.String(), nullable=True),
        sa.Column('transmission_id', sa.String(), nullable=True),
        sa.Column('power_hp', sa.Integer(), nullable=True),
        sa.Column('torque_nm', sa.Integer(), nullable=True),
        sa.Column('top_speed', sa.Integer(), nullable=True),
        sa.Column('acceleration_0_100', sa.String(), nullable=True),
        sa.Column('consumption_combined', sa.String(), nullable=True),
        sa.Column('co2_emissions', sa.Integer(), nullable=True),
        sa.Column('price_new', sa.Integer(), nullable=True),
        sa.Column('price_used_avg', sa.Integer(), nullable=True),
        sa.Column('standard_equipment', JSON, nullable=True),
        sa.Column('optional_equipment', JSON, nullable=True),
        sa.Column('year_start', sa.Integer(), nullable=True),
        sa.Column('year_end', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['model_id'], ['car_models.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['engine_id'], ['engines.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['transmission_id'], ['transmissions.id'], ondelete='SET NULL')
    )
    op.create_index('ix_technical_specifications_model_id', 'technical_specifications', ['model_id'])

    # Create brand_reviews table
    op.create_table('brand_reviews',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('brand_id', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('overall_rating', sa.Integer(), nullable=True),
        sa.Column('reliability_rating', sa.Integer(), nullable=True),
        sa.Column('quality_rating', sa.Integer(), nullable=True),
        sa.Column('value_rating', sa.Integer(), nullable=True),
        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('review_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['brand_id'], ['car_brands.id'], ondelete='CASCADE')
    )
    op.create_index('ix_brand_reviews_brand_id', 'brand_reviews', ['brand_id'])

    # Create model_reviews table
    op.create_table('model_reviews',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('model_id', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('overall_rating', sa.Integer(), nullable=True),
        sa.Column('comfort_rating', sa.Integer(), nullable=True),
        sa.Column('performance_rating', sa.Integer(), nullable=True),
        sa.Column('fuel_economy_rating', sa.Integer(), nullable=True),
        sa.Column('reliability_rating', sa.Integer(), nullable=True),
        sa.Column('quality_rating', sa.Integer(), nullable=True),
        sa.Column('value_rating', sa.Integer(), nullable=True),
        sa.Column('technology_rating', sa.Integer(), nullable=True),
        sa.Column('ownership_duration', sa.String(), nullable=True),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('usage_type', sa.String(), nullable=True),
        sa.Column('pros', JSON, nullable=True),
        sa.Column('cons', JSON, nullable=True),
        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('review_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['model_id'], ['car_models.id'], ondelete='CASCADE')
    )
    op.create_index('ix_model_reviews_model_id', 'model_reviews', ['model_id'])

    # Create engine_reviews table
    op.create_table('engine_reviews',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('engine_id', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('overall_rating', sa.Integer(), nullable=True),
        sa.Column('performance_rating', sa.Integer(), nullable=True),
        sa.Column('fuel_economy_rating', sa.Integer(), nullable=True),
        sa.Column('reliability_rating', sa.Integer(), nullable=True),
        sa.Column('refinement_rating', sa.Integer(), nullable=True),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('ownership_duration', sa.String(), nullable=True),
        sa.Column('pros', JSON, nullable=True),
        sa.Column('cons', JSON, nullable=True),
        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('review_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['engine_id'], ['engines.id'], ondelete='CASCADE')
    )
    op.create_index('ix_engine_reviews_engine_id', 'engine_reviews', ['engine_id'])

    # Create transmission_reviews table
    op.create_table('transmission_reviews',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('transmission_id', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('overall_rating', sa.Integer(), nullable=True),
        sa.Column('smoothness_rating', sa.Integer(), nullable=True),
        sa.Column('reliability_rating', sa.Integer(), nullable=True),
        sa.Column('responsiveness_rating', sa.Integer(), nullable=True),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('ownership_duration', sa.String(), nullable=True),
        sa.Column('pros', JSON, nullable=True),
        sa.Column('cons', JSON, nullable=True),
        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('review_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['transmission_id'], ['transmissions.id'], ondelete='CASCADE')
    )
    op.create_index('ix_transmission_reviews_transmission_id', 'transmission_reviews', ['transmission_id'])


def downgrade() -> None:
    """Downgrade schema - Remove car encyclopedia tables."""
    op.drop_table('transmission_reviews')
    op.drop_table('engine_reviews')
    op.drop_table('model_reviews')
    op.drop_table('brand_reviews')
    op.drop_table('technical_specifications')
    op.drop_table('car_models')
    op.drop_table('transmissions')
    op.drop_table('engines')
    op.drop_table('car_brands')
